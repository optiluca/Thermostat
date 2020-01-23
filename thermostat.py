import datetime
import logging
import sqlite3
import sys
import time
# from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler
from sqlite3 import Error
import pyowm



import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
import uuid

from telegram.ext import Updater, CommandHandler, Filters

from utils import set_boiler, read_temp, read_config


class Thermostat:
    def __init__(self, configuration_file):
        config = read_config(configuration_file)
        self.night_temp = config['temperatures']['night_temp']
        self.day_temp = config['temperatures']['day_temp']
        self.away_temp = config['temperatures']['away_temp']

        self.morning_beginning = to_time(config['times']['morning_beginning'])
        self.morning_end = to_time(config['times']['morning_end'])
        self.evening_beginning = to_time(config['times']['evening_beginning'])
        self.evening_end = to_time(config['times']['evening_end'])

        self.hysteresis = 0.5

        self.boiler_state = False

        self.logger = setup_logger()
        self.db_connection = setup_db(create_table=True)

        # OWM
        self.owm = pyowm.OWM(config['tokens']['openweathermap'], subscription_type='free')
        self.lat = config['coordinates']['latitude']
        self.lon = config['coordinates']['longitude']

        # Telegram

        self.telegram_updater = Updater(token=config['tokens']['telegram'], use_context=True)
        self.telegram_dispatcher = self.telegram_updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        self.telegram_dispatcher.add_handler(start_handler)

        status_handler = CommandHandler('status', self.status)
        self.telegram_dispatcher.add_handler(status_handler)

        set_handler = CommandHandler('set', self.set, pass_args=True,
                                     filters=Filters.user(username=["@optiluca", "@PhilosopherChef"]))
        self.telegram_dispatcher.add_handler(set_handler)

        plot_handler = CommandHandler('plot', self.plot)
        self.telegram_dispatcher.add_handler(plot_handler)

        self.telegram_updater.start_polling()

    def get_target_temp(self):
        now = datetime.datetime.now()

        weekday = now.isoweekday()
        time_of_day = now.time()

        is_weekend = weekday >= 6

        if time_of_day < self.morning_beginning:
            temp = self.night_temp
        elif time_of_day < self.morning_end:
            temp = self.day_temp
        elif time_of_day < self.evening_beginning:
            if is_weekend:
                temp = self.day_temp
            else:
                temp = self.away_temp
        elif time_of_day < self.evening_end:
            temp = self.day_temp
        else:
            temp = self.night_temp

        return temp

    def main_loop(self):
        while True:
            t_current = read_temp()
            t_target = self.get_target_temp()
            try:
                t_out = self.owm.weather_at_coords(self.lat, self.lon).get_weather().get_temperature(unit='celsius')['temp']
            except Error as e:
                print(e)
                t_out = None

            status_string = 'Target T: {}, Current T: {}, Outside T: {}'.format(t_target, t_current, t_out)
            # print(status_string)
            self.logger.info(status_string)

            if t_current > t_target + self.hysteresis:
                boiler_state = False
                b_update_state = True
            elif t_current < t_target - self.hysteresis:
                boiler_state = True
                b_update_state = True
            else:
                boiler_state = None
                b_update_state = False

            if b_update_state:
                self.boiler_state = boiler_state
                set_boiler(self.boiler_state)
                self.logger.info('Boiler state: {}'.format(self.boiler_state))

            add_row_to_db(self.db_connection, time=int(time.time()), sensor_temperature=t_current,
                          target_temperature=t_target, outside_temperature=t_out, boiler_on=self.boiler_state)

            time.sleep(30)

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hello!  This is your thermostat. Send /status for current info.  Send /set to change settings")

    def status(self, update, context):
        message_text = 'Target T: {}, Current T: {}, Boiler status: {}'.format(self.get_target_temp(), read_temp(),
                                                                               self.boiler_state)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message_text)

    def set(self, update, context):
        try:
            # args[0] should contain the thing to change, args[1] the new value
            param = context.args[0]
            value = float(context.args[1])

            if param in ['morning_beginning', 'morning_end', 'evening_beginning', 'evening_end']:
                value = to_time(value)

            setattr(self, param, value)

            update.message.reply_text('{} updated to {}'.format(param, value))

        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /set <night_temp/day_temp/away_temp, morning_beginning/morning_end/evening_beginning/evening_end>')

    def plot(self, update, context):
        now = int(time.time())
        yesterday = now - 3600*24

        # Can't use main connection as it's in a different thread!
        conn = setup_db()
        times, sensor_temps, target_temps, boiler_ons = select_data_in_range(conn, yesterday, now)

        times = [datetime.datetime.fromtimestamp(x) for x in times]
        plt.figure()
        fig, ax1 = plt.subplots()
        ax1.set_xlabel('t')
        ax1.set_ylabel('T')
        ax1.set_ylim((14, 21))
        ax1.plot(times, sensor_temps)
        ax1.plot(times, target_temps)

        ax2 = ax1.twinx()
        ax2.set_ylabel('boiler_status')
        ax2.plot(times, boiler_ons)

        fig.tight_layout()

        f_name = str(uuid.uuid4()) + '.png'
        plt.savefig(f_name)

        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(f_name, 'rb'))
        os.remove(f_name)

######################


def setup_logger(log_file='Thermostat.log', level=logging.INFO):
    # Configure log file
    l = logging.getLogger()
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, delay=False)
    # file_handler = FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)
    return l


def setup_db(db_file='Thermostat.db', create_table=False):
    # Connect
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    if create_table:
        # Create table
        create_table_sql = """CREATE TABLE IF NOT EXISTS stats (
                                time integer PRIMARY KEY,
                                sensor_temperature real NOT NULL,
                                target_temperature real NOT NULL,
                                outside_temperature real,
                                boiler_on integer NOT NULL
                            );"""

        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    return conn


def add_row_to_db(conn, time=None, sensor_temperature=None, target_temperature=None, outside_temperature=None,
                  boiler_on=None):
    row = (time, sensor_temperature, target_temperature, boiler_on, outside_temperature)
    sql = ''' INSERT INTO stats(time,sensor_temperature,target_temperature,boiler_on,outside_temperature)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, row)
    conn.commit()
    return cur.lastrowid


def select_data_in_range(conn, t_start, t_end):
    cur = conn.cursor()
    cur.execute("SELECT time,sensor_temperature,target_temperature,boiler_on FROM stats WHERE time>=? AND time<?", (t_start, t_end))

    times = []
    sensor_temps = []
    target_temps = []
    boiler_ons = []
    rows = cur.fetchall()
    for row in rows:
        times.append(row[0])
        sensor_temps.append(row[1])
        target_temps.append(row[2])
        boiler_ons.append(row[3])

    return times, sensor_temps, target_temps, boiler_ons


def to_time(t):
    if isinstance(t, int) or isinstance(t, float):
        t = str(int(t)).zfill(4)
    return datetime.datetime.strptime(t, '%H%M').time()


if __name__ == "__main__":
    print('Starting...')

    thermostat = Thermostat('config.yml')

    try:
        thermostat.main_loop()
    except KeyboardInterrupt:
        thermostat.telegram_updater.idle()
        set_boiler(False)
        sys.exit(0)
