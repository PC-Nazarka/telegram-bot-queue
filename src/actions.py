import logging

from aiogram.utils import executor

from database import init_db
from handlers import (register_handlers_admin, register_handlers_cancel_action,
                      register_handlers_client, set_commands_client)
from main import dispatcher


async def on_startup(dispatcher) -> None:
    """Action on startup app."""
    init_db()
    await set_commands_client(dispatcher)


async def on_shutdown(dispatcher) -> None:
    """Action on shutdown app."""
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


logging.basicConfig(filename="app.log")
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
register_handlers_cancel_action(dispatcher)
register_handlers_client(dispatcher)
register_handlers_admin(dispatcher)
executor.start_polling(
    dispatcher=dispatcher,
    skip_updates=True,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)
