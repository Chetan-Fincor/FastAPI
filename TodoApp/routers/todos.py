from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from ..models import Todos
from .auth import get_user_from_cookie

from pydantic import BaseModel
from starlette.responses import RedirectResponse
from ..templates_config import templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

db_dependency = Annotated[Session, Depends(get_db)]


# =========================================
# TODO MODEL
# =========================================

class TodoRequest(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool


# =========================================
# LOGIN REDIRECT
# =========================================

def redirect_to_login():
    response = RedirectResponse(
        url="/auth/login-page",
        status_code=status.HTTP_302_FOUND
    )

    response.delete_cookie("access_token")

    return response


# =========================================
# TODO PAGE
# =========================================

@router.get("/todo-page")
async def render_todo_page(
        request: Request,
        db: db_dependency
):

    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    todos = db.query(Todos).filter(
        Todos.owner_id == user["user_id"]
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={
            "request": request,
            "todos": todos,
            "user": user
        }
    )


# =========================================
# ADD TODO PAGE
# =========================================

@router.get("/add-todo-page")
async def add_todo_page(request: Request):

    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        request=request,
        name="add-todo.html",
        context={
            "request": request,
            "user": user
        }
    )


# =========================================
# EDIT TODO PAGE
# =========================================

@router.get("/edit-todo-page/{todo_id}")
async def edit_todo_page(
        request: Request,
        todo_id: int,
        db: db_dependency
):

    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    todo = db.query(Todos).filter(
        Todos.id == todo_id,
        Todos.owner_id == user["user_id"]
    ).first()

    if todo is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        request=request,
        name="edit-todo.html",
        context={
            "request": request,
            "todo": todo,
            "user": user
        }
    )


# =========================================
# CREATE TODO
# =========================================

@router.post("/todo")
async def create_todo(
        todo_request: TodoRequest,
        request: Request,
        db: db_dependency
):

    user = await get_user_from_cookie(request)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    todo = Todos(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        complete=todo_request.complete,
        owner_id=user["user_id"]
    )

    db.add(todo)
    db.commit()

    return {"message": "Todo created successfully"}


# =========================================
# UPDATE TODO
# =========================================

@router.put("/todo/{todo_id}")
async def update_todo(
        todo_id: int,
        todo_request: TodoRequest,
        request: Request,
        db: db_dependency
):

    user = await get_user_from_cookie(request)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    todo = db.query(Todos).filter(
        Todos.id == todo_id,
        Todos.owner_id == user["user_id"]
    ).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.commit()

    return {"message": "Todo updated successfully"}


# =========================================
# DELETE TODO
# =========================================

@router.delete("/todo/{todo_id}")
async def delete_todo(
        todo_id: int,
        request: Request,
        db: db_dependency
):

    user = await get_user_from_cookie(request)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    todo = db.query(Todos).filter(
        Todos.id == todo_id,
        Todos.owner_id == user["user_id"]
    ).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}