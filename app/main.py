from datetime import datetime
import random
import string

from cachetools import TTLCache
from fastapi import Cookie, Depends, FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

team_progress = TTLCache(100, 36000)
room4_code = TTLCache(100, 36000)
room4_amount = TTLCache(100, 36000)
room4_last_clicked = TTLCache(100, 36000)

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
                "black": room == 0,
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

    if key == "6721543":
        return RedirectResponse(url="/room1/answer6721543")
    else:
        return RedirectResponse(url="/room1?lockbox_failed=true")


@app.get("/room1/answer6721543")
async def room1_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved Room 1 at time {datetime.now()}")
    return answer_template(request,
            "Room 1",
            "Red Room",
            "color:red",
            'There is a note with the message: "R: 144"',
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

    print(f"Team {registry.team} has solved Room 2 at time {datetime.now()}")
    return answer_template(request,
            "Room 2",
            "Green Room",
            "color:green",
            'There is a note with the message: "G: 128"',
            'A second note has the message: "The keys to locked rooms are in RGB format."')


@app.get("/room3")
async def room3(
        request: Request,
        lockbox_failed: bool = False,
        registry: Registry = Depends(require_registry)):

        rows = [
                "NVDTHEBEAANS",
                "OIEINGITUURE",
                "CCTDASFULTAD",
                "WERNECOWENEV",
                "IINCSHNLGLVN",
                "ESULLLKEDAAO",
                "OIVETHCOMSTI",
                "ERYVENNUMENT",
                "VDIORGITYMEN",
                "OCSSEIEREYOJ"
                ]
        key1 = ["LEV", "ITI", "CUS"]
        key2 = ["ANS", "IEP", "SEH"]
        key3 = ["LAS", "GIA", "GIA"]
        return templates.TemplateResponse("room3.html",
                {
                    "request": request,
                    "lockbox_failed": lockbox_failed,
                    "rows": rows,
                    "key1": key1,
                    "key2": key2,
                    "key3": key3,
                })


@app.get("/room3/lockbox")
async def room3_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key.replace(" ","").lower() == "hellothere":
        return RedirectResponse(url="/room3/generalkenobi")
    else:
        return RedirectResponse(url="/room3?lockbox_failed=true")


@app.get("/room3/generalkenobi")
async def room3_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved Room 3 at time {datetime.now()}")
    return answer_template(request,
            "Room 3",
            "Blue Room",
            "color:blue",
            'There is a note with the message: "B: 255"',
            'A second note has the message: "The keys to locked rooms are in RGB format."')


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
        code = "Passcode: pannenkoek"
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
        keyR: str,
        keyG: str,
        keyB: str,
        locked_room: int,
        registry: Registry = Depends(require_registry)):

    def num(s):
        try:
            return int(s)
        except ValueError:
            return None

    key = (num(keyR), num(keyG), num(keyB))
    if locked_room == 4:
        if key == (0, 128, 255):
            print(f"Team {registry.team} has unlocked Room 4 at time {datetime.now()}")
            team_progress[(registry.team, locked_room)] = True
            return RedirectResponse(url="/room4")
        else:
            return RedirectResponse(url="/room4?unlock_failure=true")
    elif locked_room == 5:
        if key == (144, 0, 255):
            print(f"Team {registry.team} has unlocked Room 5 at time {datetime.now()}")
            team_progress[(registry.team, locked_room)] = True
            return RedirectResponse(url="/room5")
        else:
            return RedirectResponse(url="/room5?unlock_failure=true")
    elif locked_room == 6:
        if key == (144, 128, 0):
            print(f"Team {registry.team} has unlocked Room 6 at time {datetime.now()}")
            team_progress[(registry.team, locked_room)] = True
            return RedirectResponse(url="/room6")
        else:
            return RedirectResponse(url="/room6?unlock_failure=true")
    elif locked_room == 0:
        if key == (0, 0, 0):
            print(f"Team {registry.team} has unlocked Room 0 at time {datetime.now()}")
            team_progress[(registry.team, locked_room)] = True
            return RedirectResponse(url="/room0")
        else:
            return RedirectResponse(url="/room0?unlock_failure=true")


@app.get("/room4/lockbox")
async def room4_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "pannenkoek":
        return RedirectResponse(url="/room4/pannenkoek")
    else:
        return RedirectResponse(url="/room4?lockbox_failed=true")


@app.get("/room4/pannenkoek")
async def room4_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved Room 4 at time {datetime.now()}")
    return answer_template(request,
            "Room 4",
            "Cyan Room",
            "color:cyan",
            'There is a note with the message: "M N"',
            'A second note has the message: "Vaccine is in the Black Room."')


@app.get("/room5")
async def room5(
        request: Request,
        unlock_failure: bool = False,
        lockbox_failed: bool = False,
        start_btn_clicked: str = None,
        coordinates: str = None,
        registry: Registry = Depends(require_registry)):

    if (registry.team, 5) in team_progress:
        return templates.TemplateResponse("room5.html",
                {
                    "request": request,
                    "lockbox_failed": lockbox_failed,
                })
    else:
        return locked_room_template(request,
                "Room 5",
                "Magenta Room",
                "color:magenta",
                5,
                unlock_failure)


@app.get("/room5/lockbox")
async def room5_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "13047":
        return RedirectResponse(url="/room5/answer13047")
    else:
        return RedirectResponse(url="/room5?lockbox_failed=true")


@app.get("/room5/answer13047")
async def room5_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved Room 5 at time {datetime.now()}")
    return answer_template(request,
            "Room 5",
            "Magenta Room",
            "color:magenta",
            'There is a note with the message: "I C P"',
            'A second note has the message: "The color key in the Magenta Room matches the room number. All colored rooms have room numbers."')


@app.get("/room5/bluec")
async def bluec(
        request: Request,
        registry: Registry = Depends(require_registry)):

    return templates.TemplateResponse("bluec.html", {"request": request})


@app.get("/room6")
async def room6(
        request: Request,
        unlock_failure: bool = False,
        lockbox_failed: bool = False,
        start_btn_clicked: str = None,
        coordinates: str = None,
        registry: Registry = Depends(require_registry)):

    if (registry.team, 6) in team_progress:
        return templates.TemplateResponse("room6.html", {"request": request, "lockbox_failed": lockbox_failed})
    else:
        return locked_room_template(request,
                "Room 6",
                "Yellow Room",
                "color:#DDDD00",
                6,
                unlock_failure)


@app.get("/room6/lockbox")
async def room6_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key == "15653":
        return RedirectResponse(url="/room6/15653")
    else:
        return RedirectResponse(url="/room6?lockbox_failed=true")


@app.get("/room6/15653")
async def room6_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved Room 6 at time {datetime.now()}")
    return answer_template(request,
            "Room 6",
            "Yellow Room",
            "color:#DDDD00",
            'There is a note with the message: "A E D"',
            'A second note has the message: "Teleportation via manually adjusting the URL may be required to access the Vaccine."')


@app.get("/room0")
async def room0(
        request: Request,
        unlock_failure: bool = False,
        lockbox_failed: bool = False,
        registry: Registry = Depends(require_registry)):

    if (registry.team, 0) in team_progress:
        return templates.TemplateResponse("room0.html",
            {
                "request": request,
                "lockbox_failed": lockbox_failed,
                "lockbox_success": False,
            })
    else:
        return locked_room_template(request,
                "Room 0",
                "Black Room",
                "color:white",
                0,
                unlock_failure)


@app.get("/room0/lockbox")
async def room0_lockbox(
        request: Request,
        key: str,
        registry: Registry = Depends(require_registry)):

    if key.lower() == "pandemic":
        return RedirectResponse(url="/room0/pandemic")
    else:
        return RedirectResponse(url="/room0?lockbox_failed=true")


@app.get("/room0/pandemic")
async def room0_answer(
        request: Request,
        registry: Registry = Depends(require_registry)):

    print(f"Team {registry.team} has solved the Escape Room at time {datetime.now()}")
    code = str(registry.team) + "|" + str(datetime.now())
    return templates.TemplateResponse("vaccine.html", {"request": request, "success_code": code})
