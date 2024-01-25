from aiogram import Router

from . import client
from . import admin

def setup_callback_routers():

    router = Router()
    router.include_router(client.router)
    router.include_router(admin.router)
    return router