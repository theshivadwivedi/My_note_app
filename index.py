from fastapi import FastAPI
from routes.note import note 
from fastapi.staticfiles import StaticFiles
from routes.auth import auth
from routes.google_auth import google_auth
from starlette.middleware.sessions import SessionMiddleware
from routes.auth import SECRET_KEY


app = FastAPI()
app.include_router(note)
app.include_router(auth)
app.include_router(google_auth)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
