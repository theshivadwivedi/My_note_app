from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from bson import ObjectId
from config.db import users_collection

auth = APIRouter()
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "f47ac10b58cc4372a5670e02b2c3d4798f7a5c3e7a12e1dbe96f7d2c3b0f1a9d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# -------------------
# Password utilities
# -------------------
def hash_password(password: str):
    return pwd_context.hash(password.encode("utf-8")[:72])

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password.encode("utf-8")[:72], hashed_password)

# -------------------
# Token utilities
# -------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# -------------------
# Async current user
# -------------------
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        # Async wrapper for sync DB call
        user = await run_in_thread(lambda: users_collection.find_one({"_id": ObjectId(user_id)}))
        if not user:
            return RedirectResponse(url="/login", status_code=303)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -------------------
# Signup routes
# -------------------
@auth.get("/signup")
async def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@auth.post("/signup")
async def signup_post(request: Request):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")

    if not username or not email or not password:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "All fields required"})

    if await run_in_thread(lambda: users_collection.find_one({"email": email})):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "User already exists"})

    hashed_pw = hash_password(password)
    await run_in_thread(lambda: users_collection.insert_one({"username": username, "email": email, "password": hashed_pw}))

    return RedirectResponse("/login", status_code=303)

# -------------------
# Login routes
# -------------------
@auth.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth.post("/login")
async def login_post(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    user = await run_in_thread(lambda: users_collection.find_one({"email": email}))
    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    token = create_access_token({"sub": str(user["_id"])})
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

# -------------------
# Logout route
# -------------------
@auth.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

# -------------------
# Helper: run sync function in thread for async
# -------------------
import asyncio
def run_in_thread(func):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, func)
