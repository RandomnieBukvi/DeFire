import asyncio
from aiogram import Bot, Dispatcher, F
from config import TOKEN
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from tg_bot_buttons import menu, create_inline_markup_from_data
import logging
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from subscribe_state import Subscribe
import sqlite3

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Вас приветствует бот пожарной системы DeFire.\n\nПеред вами меню действий',
                         reply_markup=menu)


@dp.message(Command('menu'))
async def open_menu(message: Message):
    await message.answer('Перед вами меню действий', reply_markup=menu)


@dp.message(F.text == 'Подписаться на устройство')
async def start_subscribe(message: Message, state: FSMContext):
    await state.set_state(Subscribe.device_id)
    await message.answer('Введите номер вашего устройства')


@dp.message(Subscribe.device_id)
async def device_to_password(message: Message, state: FSMContext):
    await state.update_data(device_id=message.text)
    await state.set_state(Subscribe.password)
    await message.answer('Введите пароль вашего устройства')


@dp.message(Subscribe.password)
async def password_to_subscribe(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await state.clear()

    if data['device_id'] != 'test' or data['password'] != '123':
        await message.answer('Вы неправильно ввели номер или пароль от вашего устройства\n\n Вызвать меню /menu')
    else:
        db = sqlite3.connect('data.db')
        cur = db.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
             device_id text,
              subs_ids text)''')
        db.commit()

        same_device_id = cur.execute(f"SELECT subs_ids FROM devices WHERE device_id = '{data['device_id']}'").fetchall()
        if len(same_device_id) > 0:
            subs = same_device_id[0][0]
            if str(message.from_user.id) in subs:
                await message.answer('Вы уже подписаны на это устройство\n\n Вызвать меню /menu')
            else:
                if len(subs) > 0:
                    subs += f', {message.from_user.id}'
                else:
                    subs += str(message.from_user.id)
                cur.execute(f"UPDATE devices SET subs_ids = '{subs}' WHERE device_id = '{data['device_id']}'")
                #f"INSERT INTO devices (subs_ids,) WHERE device_id = '{data['device_id']}' VALUES ('{subs}',)"
                db.commit()
                await message.answer(f'Вы были успешно подписаны на устройство {data['device_id']}\n\n Вызвать меню /menu')
        else:
            cur.execute(f"INSERT INTO devices (device_id, subs_ids) VALUES ('{data['device_id']}', '{message.from_user.id}')")
            db.commit()
            await message.answer(f'Вы были успешно подписаны на устройство {data['device_id']}\n\n Вызвать меню /menu')
        # await message.answer('Выведем всю базу данных')
        # data_str = ''
        # elements = cur.execute("SELECT * FROM devices").fetchall()
        # for element in elements:
        #     data_str += f'id: {element[0]}, device_id: {element[1]}, subs_ids: {element[2]}\n'
        # await message.answer(data_str)
        cur.close()
        db.close()


@dp.message(F.text == 'Отписаться от устройства')
async def unsubscribe(message: Message):
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
         device_id text,
          subs_ids text)''')
    db.commit()

    user_devices = cur.execute(f"SELECT device_id FROM devices WHERE subs_ids LIKE '%{message.from_user.id}%'").fetchall()
    print(user_devices)
    if len(user_devices) > 0:
        user_devices_data = [el[0] for el in user_devices]
        await message.answer("Выберите от какого устройства вам отписаться из списка",
                             reply_markup=create_inline_markup_from_data(user_devices_data))
    else:
        await message.answer('Вы еще не подписаны ни на одно устройство\n\n Вызвать меню /menu')
    # if len(same_device_id) > 0:
    #     subs = same_device_id[0][0]
    #     if str(message.from_user.id) in subs:
    #         await message.answer('Вы уже подписаны на это устройство\n\n Вызвать меню /menu')
    #     else:
    #         subs += f', {message.from_user.id}'
    #         cur.execute(f"UPDATE devices SET subs_ids = '{subs}' WHERE device_id = '{data['device_id']}'")
    #         #f"INSERT INTO devices (subs_ids,) WHERE device_id = '{data['device_id']}' VALUES ('{subs}',)"
    #         db.commit()
    #         await message.answer(f'Вы были успешно подписаны на устройство {data['device_id']}')
    # else:
    #     cur.execute(f"INSERT INTO devices (device_id, subs_ids) VALUES ('{data['device_id']}', '{message.from_user.id}')")
    #     db.commit()
    #     await message.answer(f'Вы были успешно подписаны на устройство {data['device_id']}')
    # # await message.answer('Выведем всю базу данных')
    # # data_str = ''
    # # elements = cur.execute("SELECT * FROM devices").fetchall()
    # # for element in elements:
    # #     data_str += f'id: {element[0]}, device_id: {element[1]}, subs_ids: {element[2]}\n'
    # # await message.answer(data_str)
    cur.close()
    db.close()


@dp.callback_query(F.data.startswith("delete_device"))
async def delete_device(callback: CallbackQuery):
    await callback.answer()
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    device_id = callback.data[14:]
    device_subs = cur.execute(
        f"SELECT subs_ids FROM devices WHERE device_id = '{device_id}'").fetchall()
    subs = device_subs[0][0]
    subs = str(subs)
    print(subs)
    user_id = str(callback.from_user.id)
    start = subs.index(user_id)
    print(start)
    if len(subs) == user_id:
        print('ONLY ONE USER')
        cur.execute(
            f"UPDATE devices SET subs_ids = '' WHERE device_id = '{device_id}'")
        db.commit()
    else:
        if start == 0:
            subs = subs[len(user_id) + 2:]
        else:
            subs = subs[:start - 2] + subs[start + len(user_id):]
        cur.execute(
            f"UPDATE devices SET subs_ids = '{subs}' WHERE device_id = '{device_id}'")
        db.commit()
    await callback.message.answer(f'Вы успешно отписались от устройства {device_id}')
    cur.close()
    db.close()


@dp.message(Command('show_all'))
async def show_all(message: Message):
    await message.answer('Выведем всю базу данных')
    data_str = ''
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
             device_id text,
              subs_ids text)''')
    db.commit()
    elements = cur.execute("SELECT * FROM devices").fetchall()
    for element in elements:
        data_str += f'id: {element[0]}, device_id: {element[1]}, subs_ids: {element[2]}\n'
    await message.answer(data_str)
    cur.close()
    db.close()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("EXIT")
