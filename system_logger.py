import asyncio
import sqlite3
from io import BytesIO
from PIL import ImageDraw, ImageColor, Image, ImageFont
import datetime as dt
import psutil

AXIS_Y_LENGTH = 500
AXIS_X_LENGTH = 50
Y_SCALE = 5
X_SCALE= 1.5

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
            # print(now_time)
            # print('cpu', cpu)

            cursor.execute('INSERT INTO sys_log VALUES (?, ?, ?)',
                           (cpu, memory, now_time))
            con.commit()
            await asyncio.sleep(period)
        except asyncio.CancelledError:
            con.close()
            break


def get_value_from_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite')
    cursor = db_connection.cursor()
    # cursor.execute("SELECT cpu FROM sys_log")

    cursor.execute("""SELECT cpu, mem 
                      FROM sys_log
                      WHERE check_time > datetime('now','-1 hours')
                      ORDER BY check_time
                      LIMIT 720;
                      """)
    data = cursor.fetchall()
    print(len(data))
    print(data)
    return data


def make_image_by_dots(points):

    image, draw = make_draw_area()

    for i in range(len(points) - 1):
        x1 = transform_X_coord_to_asixs(i)
        x2 = transform_X_coord_to_asixs(i + 1)
        y1 = transform_Y_coord_to_asixs(points[i][0])
        y2 = transform_Y_coord_to_asixs(points[i + 1][0] )

        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb('red'))

    for i in range(len(points) - 1):
        x1 = transform_X_coord_to_asixs(i)
        x2 = transform_X_coord_to_asixs(i + 1)
        y1 = transform_Y_coord_to_asixs(points[i][1])
        y2 = transform_Y_coord_to_asixs(points[i + 1][1])

        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb('green'))

    img_file= BytesIO()
    image.save(img_file, format="PNG")
    img_file.seek(0)

    return img_file


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


def make_draw_area():
    width = 1130
    height = 550
    LINES = 720  # количество отметок в графике по 5сек

    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=ImageColor.getrgb("white"))
    # написать функцию, которая строит точку относительна нулевой координаты
    # (x = 50, y = 500)
    # и написать функцию реверсирующую OY

    draw.line((35, 500, 1130, 500), fill=ImageColor.getrgb("black")) # ось Х
    draw.line((50, 0, 50, 515), fill=ImageColor.getrgb("black"))  # ось Y
    myfont = ImageFont.truetype("arial.ttf", 20)

    draw.text((35, 505), text='0', fill=ImageColor.getrgb("black"), font=myfont)

    return image, draw

def transform_Y_coord_to_asixs(y):
    return AXIS_Y_LENGTH - (y * Y_SCALE)

def transform_X_coord_to_asixs(x):
    return AXIS_X_LENGTH + (x * X_SCALE)
