from fastapi import FastAPI
from app.farmers.router import router as router_farmers
from app.fields.router import router as router_fields
from app.users.router import router as router_users
from app.pages.router import router as router_pages
from fastapi.staticfiles import StaticFiles


app = FastAPI()


@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}


app.include_router(router_farmers)
app.include_router(router_fields)
app.include_router(router_users)
app.include_router(router_pages)

app.mount('/static', StaticFiles(directory='app/static'), 'static')
