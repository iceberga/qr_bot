from aiogram.types import Message
import cv2 as cv
import aiohttp
import numpy as np


async def get_qr_from_photo(message: Message, bot, token) -> str:
    """
    Функция обрабатывает полученное фото с QR-кодом и возвращает декодированную строку
    """
    photo = message.photo[-1]
    file_id = await bot.get_file(photo.file_id)
    photo_url = f"https://api.telegram.org/file/bot{token}/{file_id.file_path}"

    img = await download_photo(photo_url)
    qr_data = qr_reader(img)

    return qr_data


async def download_photo(photo_url: str) -> np.ndarray:
    """
    Предварительная обработка фото
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            photo_bytes = await response.read()
            image_array = np.asarray(bytearray(photo_bytes), dtype=np.uint8)

            return cv.imdecode(image_array, cv.IMREAD_COLOR)


def qr_reader(img) -> str:
    """
    Для распознавания QR-кода
    """
    detector = cv.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    return data
