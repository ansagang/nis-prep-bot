from aiogram import Router

from . import client

def setup_callback_routers():

    router = Router()
    router.include_router(client.router)
    return router