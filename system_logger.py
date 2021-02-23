import asyncio
import sqlite3
from io import BytesIO
from PIL import ImageDraw, ImageColor, Image, ImageFont
import datetime as dt
import psutil
from settings.settings import UPDATE_DATA_TIME

# Масштаб осей
Y_SCALE = 2.5
X_SCALE = 1.5
# Количество отметок по осям Х и У
LINES_COUNT = (60 / UPDATE_DATA_TIME) * 60
TOTAL_PERCENTS = 100
# Вообще, это координата начальной точки в нашей системе координат
AXIS_Y_LENGTH = TOTAL_PERCENTS * Y_SCALE + 20 # 520
AXIS_X_LENGTH = 30
# Размер картинки
IMG_WIDTH = LINES_COUNT * X_SCALE + AXIS_X_LENGTH + 20
IMG_HIGTH = TOTAL_PERCENTS * Y_SCALE + 50
# Конечная точка оси Х
X_LENGTH = LINES_COUNT * X_SCALE + AXIS_X_LENGTH

VALUE_FOR_MINS_TEXT_POSITION = (X_LENGTH - AXIS_X_LENGTH) / 12

FIVE_MIN_SCALE = 12


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
            await asyncio.sleep(period)
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            now_time = dt.datetime.now()

            cursor.execute('INSERT INTO sys_log VALUES (?, ?, ?)',
                           (cpu, memory, now_time))
            con.commit()

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
    return data


def make_image_by_dots(points: list, type_of_graphic: str,
                       type_of_statistic: str):
    """ Функция получает на вход список данных из БД
        В этом списке первый параметр - загрузка ЦПУ, второй - загрузка ОП
        в момент времени.

        Функция возвращает изображение в байтовом виде"""
    image, draw = make_draw_area(type_of_graphic)
    cpu, mem = prepare_for_paint(points)

    if type_of_statistic == 'dynamic':
        draw_dynamic_image(cpu, 'red', draw)
        # draw_dynamic_image(mem, 'green', draw)
    elif type_of_statistic == 'static':
        cpu = get_middle_values(cpu);
        # mem = get_middle_values(mem)
        draw_static_image(cpu, 'red', draw)
        # draw_static_image(mem, 'green', draw)

    img_file = BytesIO()
    image.save(img_file, format="PNG")
    img_file.seek(0)

    return img_file


def get_middle_values(values):
    buffer = []
    values_per_5_mins = 60
    i = 0
    middle_values = []
    for value in values:
        # print(values[i])
        buffer.append(values[i])
        i += 1
        if len(buffer) == values_per_5_mins:
            middle_values.append(sum(buffer) / values_per_5_mins)
            buffer.clear()
            print('middle values', len(middle_values))

    if len(middle_values) > 0:
        middle_values.append(sum(buffer) / len(buffer))
        print('middle values last', len(middle_values))
    return middle_values


def draw_static_image(data: list, color: str, draw: ImageDraw):
    x = 0
    for i in range(len(data) - 1):
        x1 = transform_x_coord_to_asixs(x)
        x2 = transform_x_coord_to_asixs(x + 60)
        y1 = transform_y_coord_to_asixs(data[i])
        y2 = transform_y_coord_to_asixs(data[i + 1])
        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb(color=color))
        x += 60


def draw_dynamic_image(data: list, color: str, draw: ImageDraw):
    """Полученные данные преобразуются в координаты ХУ, по которым
       рисуется изображение."""
    for i in range(len(data) - 1):
        x1 = transform_x_coord_to_asixs(i)
        x2 = transform_x_coord_to_asixs(i + 1)
        y1 = transform_y_coord_to_asixs(data[i])
        y2 = transform_y_coord_to_asixs(data[i + 1])

        draw.line((x1, y1, x2, y2), fill=ImageColor.getrgb(color=color))


def make_draw_area(type_of_graphic: str):
    """ Функиця рисует базовую область для графика, содержащую оси
        и прочую вспомогательную информацию"""
    image = Image.new("RGB", (int(IMG_WIDTH), int(IMG_HIGTH)))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, IMG_WIDTH, IMG_HIGTH),
                   fill=ImageColor.getrgb("white"))
    myfont = ImageFont.truetype("arial.ttf", 12)
    # ось Х
    draw.line((AXIS_X_LENGTH - 5, AXIS_Y_LENGTH,
              X_LENGTH, AXIS_Y_LENGTH),
              fill=ImageColor.getrgb("black"))
    # ось Y
    draw.line((AXIS_X_LENGTH, 0, AXIS_X_LENGTH, AXIS_Y_LENGTH + 5),
              fill=ImageColor.getrgb("black" ))

    # полосочки и циферки по оси X
    for i in range(13):
        draw.line((AXIS_X_LENGTH + (VALUE_FOR_MINS_TEXT_POSITION * (i)),
                   AXIS_Y_LENGTH - 5,
                   AXIS_X_LENGTH + (VALUE_FOR_MINS_TEXT_POSITION * (i)),
                   AXIS_Y_LENGTH + 5), fill=ImageColor.getrgb('black'))
        time_text = f'{i * 5}'
        draw.text((AXIS_X_LENGTH - 6 + (i * VALUE_FOR_MINS_TEXT_POSITION),
                  AXIS_Y_LENGTH + 10), text=time_text,
                  fill=ImageColor.getrgb("black"), font=myfont)

    for i in range(720):
        draw.line((AXIS_X_LENGTH + (X_SCALE * (i + 1)), AXIS_Y_LENGTH - 2,
                   AXIS_X_LENGTH + (X_SCALE * (i + 1)), AXIS_Y_LENGTH + 2),
                  fill=ImageColor.getrgb('blue'))

    # полосочки и циферки по оси У
    if type_of_graphic == 'cpu':
        for i in range(11):
            percent = f'{10 * i}%'
            draw.text((0, (AXIS_Y_LENGTH - 5) - 50 * i), text=percent,
                      fill=ImageColor.getrgb("black"), font=myfont)
            draw.line((AXIS_X_LENGTH - 5, AXIS_Y_LENGTH - 50 * i,
                       AXIS_X_LENGTH + 5, AXIS_Y_LENGTH - 50 * i),
                      fill=ImageColor.getrgb('black'))
    elif type_of_graphic == 'memory':
        pass
    return image, draw


def transform_y_coord_to_asixs(y: float):
    return AXIS_Y_LENGTH - (y * Y_SCALE)


def transform_x_coord_to_asixs(x: float):
    return AXIS_X_LENGTH + (x * X_SCALE)


def prepare_for_paint(data):
    """ Функция решает вопрос с недостающими данными за последний час.
     Т.е если в течении часа программа работала не всё время - в тот момент
     когда она не работала в программу заносятся нулевые значения ЦП и ОП
     ------
     Остался не решенный вопрос: если перезапускать программу быстрее чем за 5
     секунд, то мы получим данные в БД с интервалом менее 1 сек. Эти данные
     тоже отображаются на графике, и они находятся не на своём месте а также
     сбивают положение всех послеющих точке по оси Х. Эта проблема не критична,
     если не не перезапускать программу быстрее чем за 5 сек. """
    times = []

    for i in range(len(data)):
        times.append(dt.datetime.strptime(data[i][2], '%Y-%m-%d %H:%M:%S.%f'))

    # for i in range(len(times) - 1):
    #     print(times[i + 1] - times[i])

    y_mem = []
    y_cpu = []
    list_to_del = []
    inc = 0
    for i in range(len(data) - 1):
        # Если наблюдается время между данными больше 5+0.2 сек - в буффер
        # добавляется нулевое значение логированного параметра
        if times[i + 1] - times[i] > dt.timedelta(seconds=UPDATE_DATA_TIME,
                                                  milliseconds=200):
            inc += 1
            delta = ((times[i + 1] - times[i]).seconds / UPDATE_DATA_TIME)
            print((times[i + 1] - times[i]))
            for j in range(int(delta)):
                y_mem.append(0)
                y_cpu.append(0)

            y_mem.append(data[i][1])
            y_cpu.append(data[i][0])
        # # Если наткнулись на данные, у которых интервал менее 5-0.1 сек,
        # # выпиливаем эти данные и потом заполним их нулевыми. Скорее всего
        # # эти данные возникли из за слишком быстрого перезапуска программы
        elif times[i + 1] - times[i] < dt.timedelta(seconds=UPDATE_DATA_TIME-1,
                                                    milliseconds=900):
            print(('less!', times[i + 1] - times[i]))
            list_to_del.append(i + 1)
            y_mem.append(0)
            y_cpu.append(0)
        else:
            y_mem.append(data[i][1])
            y_cpu.append(data[i][0])

    if(len(data) > 1):
        last = len(data) - 1
        y_mem.append(data[last][1])
        y_cpu.append(data[last][0])

    print('not converted len" ' + str(len(data)))
    print('converted len" ' + str(len(y_mem)))
    print('inc = ', inc)
    return y_cpu, y_mem
