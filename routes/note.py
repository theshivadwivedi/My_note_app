from fastapi import APIRouter, HTTPException, Depends
from model.note import Note
from config.db import users_collection
from schema.note import noteEntity, notesEntity
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from routes.auth import get_current_user

note = APIRouter()
templates = Jinja2Templates(directory="templates")


@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request, q: str | None = Query(None)):
    # Check if user is logged in
    current_user = await get_current_user(request)
    if isinstance(current_user, RedirectResponse):
        return current_user

    # Build query for search + user restriction
    query = {"user_id": str(current_user["_id"])}
    if q:
        query["$or"] = [
            {"tittle": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]

    docs = users_collection.find(query)

    new_doc = []
    for doc in docs:
        new_doc.append({
            "id": str(doc["_id"]),
            "tittle": doc["tittle"],
            "content": doc["content"],
            "important": doc["important"],
        })

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "new_doc": new_doc, "q": q,  "current_user": current_user}
    )


@note.post("/")
async def add_note(request: Request):
    current_user = await get_current_user(request)
    if isinstance(current_user, RedirectResponse):
        return current_user

    form = await request.form()
    new_note = {
        "tittle": form.get("tittle"),
        "content": form.get("content"),
        "important": True if form.get("important") == "on" else False,
        "user_id": str(current_user["_id"]),  # ✅ Link note to logged-in user
    }
    users_collection.insert_one(new_note)
    return RedirectResponse(url="/", status_code=303)


@note.post("/delete/{note_id}")
async def delete_note(note_id: str, request: Request):
    current_user = await get_current_user(request)
    if isinstance(current_user, RedirectResponse):
        return current_user

    try:
        users_collection.delete_one({
            "_id": ObjectId(note_id),
            "user_id": str(current_user["_id"])  # ✅ Ensure ownership
        })
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    return RedirectResponse("/", status_code=303)


@note.get("/edit/{id}", response_class=HTMLResponse)
async def edit_note_page(request: Request, id: str):
    current_user = await get_current_user(request)
    if isinstance(current_user, RedirectResponse):
        return current_user

    doc = users_collection.find_one({
        "_id": ObjectId(id),
        "user_id": str(current_user["_id"])  # ✅ Only fetch user's note
    })

    if not doc:
        raise HTTPException(status_code=404, detail="Note not found")

    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "note": noteEntity(doc)}
    )


@note.post("/update/{id}")
async def update_note(id: str, request: Request):
    current_user = await get_current_user(request)
    if isinstance(current_user, RedirectResponse):
        return current_user

    form = await request.form()
    updated_data = {
        "tittle": form.get("tittle"),
        "content": form.get("content"),
        "important": "important" in form,
    }

    users_collection.update_one(
        {"_id": ObjectId(id), "user_id": str(current_user["_id"])},  # ✅ Ownership check
        {"$set": updated_data}
    )
    return RedirectResponse("/", status_code=303)
