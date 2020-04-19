import string
import random

from cachetools import TTLCache
from fastapi import Cookie, Depends, FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

team_progress = TTLCache(100, 3600)
room4_code = TTLCache(100, 3600)
room4_amount = TTLCache(100, 3600)
room4_last_clicked = TTLCache(100, 3600)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request, name: str = Cookie(None), team: int = Cookie(None)):
    data = {
        "registered": name is not None and team is not None,
        "name": name,
        "team": team
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/register")
async def register(name: str, team: int):
    response = RedirectResponse(url="/")
    response.set_cookie(key="name", value=name)
    response.set_cookie(key="team", value=team)
    return response


@app.get("/unregister")
async def unregister():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="name")
    response.delete_cookie(key="team")
    return response


class Registry:
    def __init__(self, name: str, team: int):
        self.name = name
        self.team = team


class UnregisteredException(Exception):
    pass


async def require_registry(name: str = Cookie(None), team: int = Cookie(None)):
    if name is None or team is None:
        raise UnregisteredException()
    else:
        registry = Registry(name, team)
        return registry


@app.exception_handler(UnregisteredException)
async def unregistered_handler(request: Request, ex: UnregisteredException):
    return RedirectResponse(url="/")


@app.get("/room7")
async def room7(request: Request, registry: Registry = Depends(require_registry)):
    return templates.TemplateResponse("room7.html", {"request": request})


def answer_template(request: Request, title, header, color, message1, message2):
    return templates.TemplateResponse("answer.html",
            {
                "request": request,
                "room_title": title,
                "room_header": header,
                "color": color,
                "message1": message1,
                "message2": message2,
            })


def locked_room_template(request: Request, title, header, color, room, unlock_failure):
    return templates.TemplateResponse("locked_room.html",
            {
                "request": request,
                "room_title": title,
                "room_header": header,
                "color": color,
                "room": room,
                "unlock_failure": unlock_failure,
            })


@app.get("/room1")
async def room1(
        request: Request,
        lockbox_failed: bool = False,
        registry: Registry = Depends(require_registry)):

    return templates.TemplateResponse("room1.html", {"request": request, "lockbox_failed": lockbox_failed})


@app.get("/room1/lockbox")
async def room1_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "13407":
        return RedirectResponse(url="/room1/answer13407")
    else:
        return RedirectResponse(url="/room1?lockbox_failed=true")


@app.get("/room1/answer13407")
async def room1_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    return answer_template(request,
            "Room 1",
            "Red Room",
            "color:red",
            'There is a note with the message: "R: 5"',
            'A second note has the message: "The keys to locked rooms are in RGB format."')


@app.get("/room2")
async def room2(
        request: Request,
        lockbox_failed: bool = False,
        registry: Registry = Depends(require_registry)):

    return templates.TemplateResponse("room2.html", {"request": request, "lockbox_failed": lockbox_failed})


@app.get("/room2/lockbox")
async def room2_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "59487500":
        return RedirectResponse(url="/room2/answer59487500")
    else:
        return RedirectResponse(url="/room2?lockbox_failed=true")


@app.get("/room2/answer59487500")
async def room2_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    return answer_template(request,
            "Room 2",
            "Green Room",
            "color:green",
            'There is a note with the message: "G: 1"',
            'A second note has the message: "The White Room has doors with the same colors..."')


@app.get("/room4")
async def room4(
        request: Request,
        unlock_failure: bool = False,
        lockbox_failed: bool = False,
        start_btn_clicked: str = None,
        coordinates: str = None,
        registry: Registry = Depends(require_registry)):

    if (registry.team, 4) in team_progress:
        message = None
        message_color = "color:black"
        show_start = False
        if start_btn_clicked:
            if registry.team not in room4_amount:
                clear_room4_state(registry)
                message = next_room4_state(registry)
        else:
            if registry.team in room4_amount:
                if coordinates is None:
                    pass
                elif registry.name == room4_last_clicked[registry.team]:
                    message = "Error! Assistance is required."
                    message_color = "color:red"
                    show_start = True
                    clear_room4_state(registry)
                elif coordinates != room4_code[registry.team]:
                    message = "Error! Incorrect."
                    message_color = "color:red"
                    show_start = True
                    clear_room4_state(registry)
                else:
                    message = next_room4_state(registry)
            else:
                # First time in room
                show_start = True
        return templates.TemplateResponse("room4.html",
                {
                    "request": request,
                    "lockbox_failed": lockbox_failed,
                    "chars": string.ascii_uppercase[:10],
                    "show_start": show_start,
                    "message": message,
                    "message_color": message_color,
                })
    else:
        return locked_room_template(request,
                "Room 4",
                "Cyan Room",
                "color:cyan",
                4,
                unlock_failure)


def next_room4_state(registry: Registry):
    room4_last_clicked[registry.team] = registry.name
    if registry.team in room4_amount:
        room4_amount[registry.team] += 1
    else:
        room4_amount[registry.team] = 0
    if room4_amount[registry.team] >= 10:
        code = "Passcode: 167324"
    else:
        code = random.choice(string.ascii_uppercase[:10]) + str(random.randint(1, 10))
    room4_code[registry.team] = code
    return code


def clear_room4_state(registry: Registry):
    if registry.team in room4_amount:
        del room4_amount[registry.team]
    if registry.team in room4_code:
        del room4_code[registry.team]
    if registry.team in room4_last_clicked:
        del room4_last_clicked[registry.team]


@app.get("/locked_room")
async def locked_room_verifier(
        key: str,
        locked_room: int,
        registry: Registry = Depends(require_registry)):

    if locked_room == 4:
        if key == "019":
            team_progress[(registry.team, locked_room)] = True
            return RedirectResponse(url="/room4")
        else:
            return RedirectResponse(url="/room4?unlock_failure=true")


@app.get("/room4/lockbox")
async def room4_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "167324":
        return RedirectResponse(url="/room4/answer167324")
    else:
        return RedirectResponse(url="/room4?lockbox_failed=true")


@app.get("/room4/answer167324")
async def room4_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    return answer_template(request,
            "Room 4",
            "Cyan Room",
            "color:cyan",
            'There is a note with the message: "M N"',
            'A second note has the message: "The color key in the Red Room matches the room number."')
