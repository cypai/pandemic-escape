from cachetools import TTLCache
from fastapi import Cookie, FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

sessions = TTLCache(100, 3600)

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


@app.get("/room7")
async def room7(request: Request):
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
async def room1(request: Request, lockbox_failed: bool = False):
    return templates.TemplateResponse("room1.html", {"request": request, "lockbox_failed": lockbox_failed})


@app.get("/room1/lockbox")
async def room1_lockbox(request: Request, key: str):
    if key == "13407":
        return RedirectResponse(url="/room1/answer13407")
    else:
        return RedirectResponse(url="/room1?lockbox_failed=true")


@app.get("/room1/answer13407")
async def room1_answer(request: Request):
    return answer_template(request,
            "Room 1",
            "Red Room",
            "color:red",
            'There is a note with the message: "R: 5"',
            'A second note has the message: "The keys to locked rooms are in RGB format."')


@app.get("/room2")
async def room2(request: Request, lockbox_failed: bool = False):
    return templates.TemplateResponse("room2.html", {"request": request, "lockbox_failed": lockbox_failed})


@app.get("/room2/lockbox")
async def room2_lockbox(request: Request, key: str):
    if key == "59487500":
        return RedirectResponse(url="/room2/answer59487500")
    else:
        return RedirectResponse(url="/room2?lockbox_failed=true")


@app.get("/room2/answer59487500")
async def room2_answer(request: Request):
    return answer_template(request,
            "Room 2",
            "Green Room",
            "color:green",
            'There is a note with the message: "G: 1"',
            'A second note has the message: "The White Room has doors with the same colors..."')


@app.get("/room4")
async def room4(request: Request, unlock_failure: bool = False):
    return locked_room_template(request,
            "Room 4",
            "Cyan Room",
            "color:cyan",
            4,
            unlock_failure)


@app.get("/locked_room")
async def locked_room_verifier(key: str, locked_room: str):
    if locked_room == "4":
        if key == "019":
            return RedirectResponse(url="/room4/019")
        else:
            return RedirectResponse(url="/room4?unlock_failure=true")
