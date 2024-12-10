from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

