from fastapi import FastAPI, Query, Form, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from dataclasses import dataclass

# Для бази даних
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(debug=True)

# Статичні файли
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблони
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)

    return templates.TemplateResponse("users.html", {"request": request, "users": users})


# Add user FORM
@app.get("/user/add/")
def add_get(request: Request):

    return templates.TemplateResponse("user_add.html", {"request": request})


# Add user POST
@app.post("/user/add/")
def add_user(login: str = Form(), name: str = Form(), surname: str = Form(), age: int = Form(ge=14), db: Session = Depends(get_db), request: Request = None):
    errors = []
    if age < 14:
        errors.append('Вік повинен бути більше 14 років')
    if len(errors) == 0:    
        crud.create_user(db=db, user=schemas.UserCreate(login=login, name=name, surname=surname, age=age)) 
        return RedirectResponse("/", status_code=303)
    else:
        return templates.TemplateResponse("user_add.html", {"request": request, "errors": errors})


# Edit user FORM
@app.get("/user/edit/{user_id}")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(user_id=user_id, db=db)

    return templates.TemplateResponse("user_edit.html", {"request": request, "user": user})

@app.post("/user/edit/{user_id}")
def edit_user(user_id: int, db: Session = Depends(get_db), login: str = Form(), name: str = Form(), surname: str = Form(), age: int = Form()):
    user = schemas.User(id=user_id, login=login, name=name, surname=surname, age=age)
    crud.update_user(user=user, db=db)

    return RedirectResponse("/", status_code=303)



@app.get("/user/delete/{user_id}")
def delete_item(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(user_id=user_id, db=db)

    return RedirectResponse("/", status_code=303)