from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from fastapi.templating import Jinja2Templates
from config.db import users_collection
from bson import ObjectId
import os

config = Config(".env")

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str, default="your_default_secret_key")

templates = Jinja2Templates(directory="templates")
google_auth = APIRouter()

# OAuth setup
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        "scope": "openid email profile"
    }
)

@google_auth.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_auth_callback")
    print("Redirect URI:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@google_auth.get("/auth/google/callback")
async def google_auth_callback(request: Request):
    try:
        # Get token
        token = await oauth.google.authorize_access_token(request)

        # ✅ FIX: Use userinfo endpoint instead of parse_id_token
        user_info = await oauth.google.userinfo(token=token)
        print("Google user info:", user_info)

        # Check if user already exists
        user = users_collection.find_one({"email": user_info["email"]})

        if not user:
            try:
                inserted = users_collection.insert_one({
                    "username": user_info.get("name", "No Name"),
                    "email": user_info["email"],
                    "password": None,
                    "google_login": True
                })
                user_id = inserted.inserted_id
                user = users_collection.find_one({"_id": user_id})  # update user ref
                print("Inserted user_id:", user_id)
            except Exception as e:
                print("MongoDB insertion error:", e)
                raise HTTPException(status_code=500, detail="User creation failed")

        # Generate JWT token
        from routes.auth import create_access_token
        access_token = create_access_token({"sub": str(user["_id"])})

        response = RedirectResponse(url="/")
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response

    except Exception as e:
        print("Google Auth Error:", e)
        raise HTTPException(status_code=400, detail="Google authentication failed")
