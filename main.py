import json
import os
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from pydantic import BaseModel
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
IMAGES_DIRECTORY = "images"
POSTS_DIRECTORY = "posts"

app.mount("/static", StaticFiles(directory="templates/styles/"), name="styles")
app.mount("/static_scripts", StaticFiles(directory="templates/scripts"), name="scripts")
app.mount("/images", StaticFiles(directory="images/"), name="images")

class UploadPost(BaseModel):
    id: int
    name: str
    description: str

    @staticmethod
    def parse_form(
        id: Annotated[int, Form()],
        name: Annotated[str, Form()],
        description: Annotated[str, Form()],
    ):
        return UploadPost(id=id, name=name, description=description)

@app.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/create_post")
async def create_post(request: Request):
    return templates.TemplateResponse("upload_page.html", {"request": request})


@app.post("/upload")
async def upload_post(post: UploadPost = Depends(UploadPost.parse_form), image: UploadFile = File(...)):

    # Логирование полученных данных для отладки
    print(f"ID: {post.id}")
    print(f"Name: {post.name}")
    print(f"Description: {post.description}")
    print(f"Filename: {image.filename}")
    print(f"Content Type: {image.content_type}")

    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="File type not supported")

    image_location = f"{IMAGES_DIRECTORY}/{image.filename}"
    with open(image_location, "wb+") as file_object:
        file_object.write(await image.read())

    post_location = f"{POSTS_DIRECTORY}/{post.id}.json"
    data_dump = jsonable_encoder(post)
    data_dump["image_url"] = image_location
    with open(post_location, "w+") as post_object:
        json.dump(data_dump, post_object)

    return RedirectResponse("/gallery", status_code=302)


@app.get("/gallery")
async def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})

@app.get("/get_post_data/{id}")
async def get_post_data(id: int):
    with open(f"posts/{id}.json", "r") as file:
        data = json.load(file)
    return data

@app.get("/posts")
async def get_posts():
    return os.listdir("posts/")


@app.get("/posts/{post_id}")
async def show_post(request: Request, post_id: int):
    post_path = f'posts/{post_id}.json'

    # Проверяем, существует ли файл
    if os.path.exists(post_path):
        # Загружаем данные поста из JSON-файла
        with open(post_path, 'r') as file:
            post_data = json.load(file)

        # Рендерим страницу с постом
        return templates.TemplateResponse("post.html", {"request": request, "post": post_data})
    else:
        # Если файл не найден, возвращаем ошибку 404
        raise HTTPException(status_code=404, detail="Post not found")