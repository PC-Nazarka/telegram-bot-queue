from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import UserActions
from services import check_user


class EditAccountInfo(StatesGroup):
    """FSM for edit account."""

    email = State()
    full_name = State()


async def start_get_info(message: types.Message) -> None:
    """Entrypoint for edit account."""
    await EditAccountInfo.email.set()
    await message.answer(
        "Введи свой email (для отправки позиции в очереди), либо 'skip'"
    )


async def input_email(message: types.Message, state: FSMContext) -> None:
    """Get info about email."""
    async with state.proxy() as data:
        data["email"] = message.text
    await EditAccountInfo.next()
    await message.answer(
        "Введи свое фамилию и имя"
    )


async def input_full_name(message: types.Message, state: FSMContext) -> None:
    """Get info about first and last name."""
    async with state.proxy() as data:
        data["full_name"] = message.text
    new_info = {
        "id": message.from_user.id,
        "full_name": data["full_name"],
        "email": "" if data["email"] == "skip" else data["email"],
    }
    UserActions.edit_user(message.from_user.id, new_info)
    await message.answer("Ваши данные успешно заменены")
    await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """Handler for cancel edit account."""
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer("Изменение данных отменено")
        await state.finish()


def register_handlers_change_account(dispatcher: Dispatcher) -> None:
    """Register handlers for change account."""
    dispatcher.register_message_handler(
        start_get_info,
        lambda message: check_user(message.from_user.id),
        commands=["change_profile"],
        state=None,
    )
    dispatcher.register_message_handler(
        input_email,
        lambda message: check_user(message.from_user.id),
        state=EditAccountInfo.email,
    )
    dispatcher.register_message_handler(
        input_full_name,
        lambda message: check_user(message.from_user.id),
        state=EditAccountInfo.full_name,
    )
    dispatcher.register_message_handler(
        cancel_handler,
        lambda message: check_user(message.from_user.id),
        state="*",
        commands="Отмена",
    )
    dispatcher.register_message_handler(
        cancel_handler,
        lambda message: check_user(message.from_user.id),
        Text(equals="Отмена", ignore_case=True),
        state="*",
    )