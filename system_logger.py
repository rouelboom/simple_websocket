import asyncio
import sqlite3
from io import BytesIO
from PIL import ImageDraw, ImageColor, Image, ImageFont
import datetime as dt
import psutil

AXIS_Y_LENGTH = 500
AXIS_X_LENGTH = 50

Y_SCALE = 5
X_SCALE = 1.5

IMG_WIDTH = 1130
IMG_HIGTH = 550

def init_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite',
                                     detect_types=sqlite3.PARSE_DECLTYPES |
                                                  sqlite3.PARSE_COLNAMES
                                    )

    cursor = db_connection.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS 'sys_log' (
                   'cpu' REAL(3),
                   'mem' REAL(3),
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

    last_hour = dt.datetime.now() - dt.timedelta(hours=1)
    s = ("SELECT * FROM sys_log "
         "WHERE check_time >= ? "
         "ORDER BY check_time;")
    cursor.execute(s, [last_hour])

    data = cursor.fetchall()
    print(len(data))
    return data


def make_image_by_dots(points: list):
    """ Функция получает на вход список данных из БД
        В этом списке первый параметр - загрузка ЦПУ, второй - загрузка ОП
        в момент времени.
        Полученные данные преобразуются в координаты ХУ, по которым
        рисуется изображение.
        Функция возвращает изображение в байтовом виде"""
    image, draw = make_draw_area()
    prepare_for_paint(points)

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
    """ Функиця рисует базовую область для графика, содержащую оси
        и прочую вспомогательную информацию"""
    image = Image.new("RGB", (IMG_WIDTH, IMG_HIGTH))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, IMG_WIDTH, IMG_HIGTH), fill=ImageColor.getrgb("white"))

    draw.line((AXIS_X_LENGTH - 15, AXIS_Y_LENGTH, IMG_WIDTH - 50, AXIS_Y_LENGTH),
              fill=ImageColor.getrgb("black")) # ось Х
    draw.line((AXIS_X_LENGTH, 0, AXIS_X_LENGTH, AXIS_Y_LENGTH + 15),
              fill=ImageColor.getrgb("black"))  # ось Y
    myfont = ImageFont.truetype("arial.ttf", 20)

    draw.text((35, 505), text='0', fill=ImageColor.getrgb("black"), font=myfont)

    return image, draw


def transform_Y_coord_to_asixs(y: float):
    return AXIS_Y_LENGTH - (y * Y_SCALE)


def transform_X_coord_to_asixs(x: float):
    return AXIS_X_LENGTH + (x * X_SCALE)


def prepare_for_paint(data):
    times = []

    for i in range(len(data)):
        times.append(data[i][2])

    # for i in range(len(times) - 2):
        # print(times[i + 2] - times[i])