import asyncio
import sqlite3
from io import BytesIO
from PIL import ImageDraw, ImageColor, Image
import datetime as dt
import psutil
import pathlib
import os


def init_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite')
    cursor = db_connection.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS 'sys_log' (
                   'cpu' real(3),
                   'mem' real(3),
                   'check_time' datetime)
                   ''')

    return db_connection, cursor


async def system_log_process(period=5):
    while True:
        try:
            con, cursor = init_database()
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            now_time = dt.datetime.now()
            # print('memory', memory)
            print('cpu', cpu)
            # print('now is: ', now_time)
            cursor.execute('INSERT INTO sys_log VALUES (?, ?, ?)',
                           (cpu, memory, now_time))
            con.commit()
            # time.sleep(period)
            await asyncio.sleep(period)
        except KeyboardInterrupt:
            con.close()


def get_value_from_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite')
    cursor = db_connection.cursor()
    cursor.execute("SELECT cpu FROM sys_log")
    cpu = cursor.fetchall()
    # print(cpu)
    return cpu


def make_image_by_dots(points):

    image, draw = make_draw_area()
    x = 0
    for point in points:
        draw.point((x, point[0] * 10), fill=ImageColor.getrgb("red"))
        x += 10

    x = 0
    for i in range(len(points) - 1):
        draw.line((x, points[i][0]* 10, x + 10, points[i + 1][0]* 100),
                  fill=ImageColor.getrgb("red"))
        x += 10

    fp = BytesIO()

    image.save("templates/graphic.jpg", "JPEG")
    image.save(fp, format="PNG")
    fp.seek(0)
    # path_to_image = os.path.abspath('templates/graphic.jpg')
    # print(path_to_image)
    # print(os.path.abspath('templates/graphic.png'))
    # return image, path_to_image
    return fp


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


def make_draw_area():
    width = 700
    height = 700
    LINES = 720  # количество отметок в графике по 5сек

    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=ImageColor.getrgb("white"))
    # тут надо преобразовать точки в систему координат нашего графика

    draw.line((50, 1000, 1050, 1000), fill=ImageColor.getrgb("black")) # ось Х
    draw.line((50, 0, 50, 1000), fill=ImageColor.getrgb("black"))  # ось Y
    draw.text((10, 10), text='text', fill=ImageColor.getrgb("black"))

    return image, draw