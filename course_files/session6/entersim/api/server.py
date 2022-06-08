from fastapi import FastAPI
from .routers import control, enterprise

app = FastAPI()

for router in control.routers + enterprise.routers:
    app.include_router(router)
