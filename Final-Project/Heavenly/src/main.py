from fastapi import FastAPI
import schemas
from repositories.database import engine
from routers import users, locations, auth, properties
import models

app = FastAPI()

models.Base.metadata.create_all(bind= engine)

app.include_router(users.router)
app.include_router(locations.router)
app.include_router(auth.router)
app.include_router(properties.router)