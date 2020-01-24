import datetime
import os
import sys
import time
import uuid
import logging
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils import to_time, try_read_config
from telegram.ext import Updater, CommandHandler, Filters
from logging.handlers import TimedRotatingFileHandler


class ThermostatService:
    def __init__(self, configuration_file):
        config = try_read_config(configuration_file)
        self.logger = self.__setup_logger()

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
        pass

    # status_string = 'Target T: {}, Current T: {}, Outside T: {}'.format(self.targetTemp, self.feedbackTemp,
    #                                                                    self.ambientTemp)
    # self.logger.info(status_string)

    # self.logger.info('Boiler state: {}'.format(self.boilerActive))

    # self.databaseLoggingService.add_row_to_db(self.feedbackTemp, self.targetTemp, self.ambientTemp,
    #                                          self.boilerActive)
    # time.sleep(30)

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
        yesterday = now - 3600 * 24

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

    def __setup_logger(log_file='Thermostat.log', level=logging.INFO):
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


if __name__ == "__main__":
    print('Starting...')

    thermostat = Thermostat('config.yml')

    try:
        thermostat.main_loop()
    except KeyboardInterrupt:
        thermostat.telegram_updater.idle()
        set_boiler(False)
        sys.exit(0)
