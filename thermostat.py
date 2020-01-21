import datetime
import logging
import sys
import time
# from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler

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

        self.hysteresis = 1

        self.boiler_state = None

        self.logger = setup_logger()

        self.telegram_updater = Updater(token=config['tokens']['telegram'], use_context=True)
        self.telegram_dispatcher = self.telegram_updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        self.telegram_dispatcher.add_handler(start_handler)

        status_handler = CommandHandler('status', self.status)
        self.telegram_dispatcher.add_handler(status_handler)

        set_handler = CommandHandler('set', self.set, pass_args=True, filters=Filters.user(username=["@optiluca", "@PhilosopherChef"]))
        self.telegram_dispatcher.add_handler(set_handler)

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

            status_string = 'Target T: {}, Current T: {}'.format(t_target, t_current)
            # print(status_string)
            self.logger.info(status_string)

            if t_current > t_target + self.hysteresis:
                self.boiler_state = False
            elif t_current < t_target - self.hysteresis:
                self.boiler_state = True
            else:
                self.boiler_state = None

            if self.boiler_state is not None:
                set_boiler(self.boiler_state)
                self.logger.info('Boiler state: {}'.format(self.boiler_state))

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
        """Add a job to the queue."""
        chat_id = update.message.chat_id
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
