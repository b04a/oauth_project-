from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import requests
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CLIENT_ID = "52817206"
CLIENT_SECRET = "jnxRw6j7YWmSgk0ewFZz"
REDIRECT_URI = "https://f791-178-204-45-119.ngrok-free.app/callback"  # Временно для локального тестирования
VK_AUTH_URL = "https://oauth.vk.com/authorize"
VK_TOKEN_URL = "https://oauth.vk.com/access_token"
VK_API_URL = "https://api.vk.com/method/users.get"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login_yandex")
async def login():
    return {"oauth": "yandex"}

@app.get("/login_vk")
async def login():
    return RedirectResponse(
        url=f"{VK_AUTH_URL}?client_id={CLIENT_ID}&display=page&redirect_uri={REDIRECT_URI}&response_type=code&v=5.131")

@app.get("/callback")
async def callback(request: Request, code: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            VK_TOKEN_URL,
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI
            }
        )
        token_data = response.json()

        # Проверка на наличие ошибок
        if "error" in token_data:
            print(f"Error getting access token: {token_data['error']}")
            return {"error": token_data["error"]}

        access_token = token_data.get("access_token")

        # Получение информации о пользователе
        user_response = await client.get(
            VK_API_URL,
            params={
                "access_token": access_token,
                "v": "5.131"
            }
        )
        user_data = user_response.json()

        # Проверка на наличие ошибок
        if "error" in user_data:
            print(f"Error getting user data: {user_data['error']}")
            return {"error": user_data["error"]}

        # Извлечение first_name и last_name
        if "response" in user_data and len(user_data["response"]) > 0:
            user_info = user_data["response"][0]
            first_name = user_info.get("first_name")
            last_name = user_info.get("last_name")

            # Вывод в терминал
            print(f"First Name: {first_name}, Last Name: {last_name}")

            return templates.TemplateResponse("greeting_vk.html",
                                              {"request": request, "username": first_name + " " + last_name})

        return user_data
