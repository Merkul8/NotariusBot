import requests
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.filters import CommandObject



BOT_TOKEN = '6607905600:AAFMvnZJMZ-oIRj14Jfv5j6Ym1QjasAAs8g'
API_URL = 'https://notariat.ru/api/probate-cases/eis-proxy'

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


@dp.message(F.text == '/start')
async def start(message: Message):
    await message.answer("Привет! Отправь мне команду /name_and_date и затем в этом же сообщении введи ФИО и дату рождения в формате 'ФИО ддммгггг', например 'Иванов Иван Иванович 01011990'")

# Скрипт, который берет данные с сервера post запросом
def get_response_json(url, json):
    with requests.Session() as session:
        with session.post(url, json=json) as response:
            data = response.json()
            return data

# Основная работа бота, отправка данных пользователю
@dp.message(Command("name_and_date"))
async def cmd_name(message: types.Message, command: CommandObject,):
    # Проверяем на наличие ФИО и даты рождения
    if command.args:
        start_data = command.args.split()
        if len(start_data) == 3:
            fio = ' '.join(start_data)
            birth_day = 'NULL'
        elif len(start_data) == 4:
            fio = ' '.join(start_data[:3])
            birth_day = start_data[-1]
    else:
        await message.answer("Пожалуйста, укажи ФИО или ФИО и дату рождения наследодателя после введения команды /name_and_answer!")
    json = {
    'birth_date': f'{birth_day}',
    'name': f'{fio}'
    }
    url = 'https://notariat.ru/api/probate-cases/eis-proxy'
    # Получение словаря со всеми данными
    data = get_response_json(url, json)
    count = data['count']
    if count > 3:
        records = data['records']
        chambers = []
        for i in records:
            chambers.append(i['ChamberName'])
        uniq_chamber = set(chambers)
        # Записываем данные, сортируя по ChamberName
        with open('result.html', 'w', encoding='utf-8') as f:
            for j in uniq_chamber:
                f.write(f'<h2>{j}</h2>')
                for i in range(0, count):
                    if j == records[i]['ChamberName']:
                        birthd_d = records[i]['BirthDate']
                        # Форматирование даты рождения
                        if birthd_d == '0':
                            birthd_d = birthd_d
                        else:
                            birthd_d = f"{birthd_d[6:8]}.{birthd_d[4:6]}.{birthd_d[:4]}"
                        deathd_d = records[i]['DeathDate']
                        # Форматирование даты смерти
                        if deathd_d == '0':
                            deathd_d = deathd_d
                        else:
                            deathd_d = f"{deathd_d[6:8]}.{deathd_d[4:6]}.{deathd_d[:4]}"
                        address = records[i]['Address']
                        district = records[i]['DistrictName']
                        # Запись в HTML файл
                        f.write(f'<div style="margin-left: 25px"><b> • </b><span>Дата рождения: {birthd_d}</span>, <span>Дата смерти: {deathd_d}</span>, <span>Адрес прописки: {address}</span>, <span>Район нотариуса: {district}</span></div><br>')
        res_file = FSInputFile(filename="result.html", path=r"C:\Users\Merkul\Desktop\bot_avangard\result.html")
        # Отправка файла
        await message.answer_document(res_file, caption=f'Результат [{count}]', reply_markup=types.ReplyKeyboardRemove(selective=True))
    else:
        for i in range(0, count):
            birthd_d = data['records'][i]['BirthDate']
            # Форматирование даты рождения
            if birthd_d == '0':
                birthd_d = birthd_d
            else:
                birthd_d = f"{birthd_d[6:8]}.{birthd_d[4:6]}.{birthd_d[:4]}"
            deathd_d = data['records'][i]['DeathDate']
            # Форматирование даты смерти
            if deathd_d == '0':
                deathd_d = deathd_d
            else:
                deathd_d = f"{deathd_d[6:8]}.{deathd_d[4:6]}.{deathd_d[:4]}"
            address = data['records'][i]['Address']
            district = data['records'][i]['DistrictName']
            chamber = data['records'][i]['ChamberName']
            res = f"{i + 1}) Дата рождения: {birthd_d},\nДата смерти: {deathd_d},\nДомашний адрес: {address},\nРайон нотариуса: {district}({chamber})"
            await message.answer(res)
   
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
