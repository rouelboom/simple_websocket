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

IMG_WIDTH = 1180
IMG_HIGTH = 550


def init_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite',
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                    sqlite3.PARSE_COLNAMES)

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
    # print(len(data))
    return data


def make_image_by_dots(points: list):
    """ Функция получает на вход список данных из БД
        В этом списке первый параметр - загрузка ЦПУ, второй - загрузка ОП
        в момент времени.
        Полученные данные преобразуются в координаты ХУ, по которым
        рисуется изображение.
        Функция возвращает изображение в байтовом виде"""
    image, draw = make_draw_area()
    cpu, mem = prepare_for_paint(points)

    for i in range(len(cpu) - 1):

        x1 = transform_x_coord_to_asixs(i)
        x2 = transform_x_coord_to_asixs(i + 1)
        y1 = transform_y_coord_to_asixs(cpu[i])
        y2 = transform_y_coord_to_asixs(cpu[i + 1])

        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb('red'))

    for i in range(len(mem) - 1):
        x1 = transform_x_coord_to_asixs(i)
        x2 = transform_x_coord_to_asixs(i + 1)
        y1 = transform_y_coord_to_asixs(mem[i])
        y2 = transform_y_coord_to_asixs(mem[i + 1])

        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb('green'))

    img_file = BytesIO()
    image.save(img_file, format="PNG")
    img_file.seek(0)

    return img_file


def make_draw_area():
    """ Функиця рисует базовую область для графика, содержащую оси
        и прочую вспомогательную информацию"""
    image = Image.new("RGB", (IMG_WIDTH, IMG_HIGTH))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, IMG_WIDTH, IMG_HIGTH),
                   fill=ImageColor.getrgb("white"))

    draw.line((AXIS_X_LENGTH - 15, AXIS_Y_LENGTH,
              IMG_WIDTH - 50, AXIS_Y_LENGTH),
              fill=ImageColor.getrgb("black"))  # ось Х
    draw.line((AXIS_X_LENGTH, 0, AXIS_X_LENGTH, AXIS_Y_LENGTH + 15),
              fill=ImageColor.getrgb("black"))  # ось Y
    myfont = ImageFont.truetype("arial.ttf", 20)

    draw.text((35, 505), text='0', fill=ImageColor.getrgb("black"), font=myfont)

    return image, draw


def transform_y_coord_to_asixs(y: float):
    return AXIS_Y_LENGTH - (y * Y_SCALE)


def transform_x_coord_to_asixs(x: float):
    return AXIS_X_LENGTH + (x * X_SCALE)


def prepare_for_paint(data):
    """ Функция решает вопрос с недостающими данными за последний час """
    times = []

    for i in range(len(data)):
        times.append(dt.datetime.strptime(data[i][2], '%Y-%m-%d %H:%M:%S.%f'))

    y_mem = []
    y_cpu = []
    a = 0
    b = 0
    if(len(data) < 720):
        for i in range(len(data) - 1):
            # Если наблюдается время между данными больше 6(доп.секунда
            # на асинхронные операции) сек - в буффер
            # добавляется нулевое значение логированного параметра
            if times[i + 1] - times[i] > dt.timedelta(seconds=6):
                b += 1
                # print('b=', b)
                # print((times[i + 1] - times[i]))
                delta = ((times[i + 1] - times[i]).seconds / 5)
                # print('delta' + str(delta))
                for j in range(int(delta)):
                    a += 1
                    # print('a=', a)
                    y_mem.append(0)
                    y_cpu.append(0)
            y_mem.append(data[i][1])
            y_cpu.append(data[i][0])

        last = len(data) - 1
        y_mem.append(data[last][1])
        y_cpu.append(data[last][0])

        # print(len(y_mem))
        # print(len(y_cpu))
        return y_cpu, y_mem

    return data[0], data[1]
