import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import initiate_db, get_all_products

initiate_db()

products = get_all_products()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb1 = ReplyKeyboardMarkup()
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button5 = KeyboardButton(text='Купить')
kb1.add(button1)
kb1.add(button2)
kb1.add(button5)

kb2 = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb2.add(button3)
kb2.add(button4)

kb3 = InlineKeyboardMarkup()
button6 = InlineKeyboardButton(text='Продуктивин', callback_data='product_buying')
button7 = InlineKeyboardButton(text='UrbanУчизм', callback_data='product_buying')
button8 = InlineKeyboardButton(text='Боттизмулин', callback_data='product_buying')
button9 = InlineKeyboardButton(text='Батарейквизм', callback_data='product_buying')
kb3.add(button6, button7, button8, button9)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    # Получаем список файлов в папке 'file'
    files = []
    for _, _, filenames in os.walk('file'):
        files.extend(filenames)

    # Проходим по списку продуктов и файлов одновременно
    for product, filename in zip(products, files):
        full_path = os.path.join('file', filename)
        with open(full_path, 'rb') as img:
            # Используем данные из базы данных для формирования сообщения
            await message.answer(
                text=f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}"
            )
            await message.answer_photo(img)

    await message.answer('Выберите продукт для покупки', reply_markup=kb3)


@dp.callback_query_handler(text=['product_buying'])
async def send_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=kb2)


@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост(см)')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес(кг)')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    norma_calories = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Ваши параметры:\n'
                         f'-Возраст = {data["age"]}лет\n'
                         f'-Рост = {data["growth"]}см\n'
                         f'-Вес = {data["weight"]}кг\n'
                         f'Ваша норма каллорий: {norma_calories}')
    await state.finish()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет!', reply_markup=kb1)


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
