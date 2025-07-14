from pyrogram import Client


def register_all(app: Client):
    from . import start, admin, autodelete, broadcast

    start.register(app)
    admin.register(app)
    autodelete.register(app)
    broadcast.register(app)
