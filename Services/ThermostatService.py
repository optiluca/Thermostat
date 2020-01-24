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
from Models import Thermostat as TH
from Services import DatabaseLoggingService as DLS

REFRESH_PERIOD = 30


class ThermostatService:
    def __init__(self, configuration_file):
        self.logger = self.__setup_logger()

        config = try_read_config(configuration_file)

        self.thermostat = TH.Thermostat(config)
        self.databaseLoggingService = DLS.DatabaseLoggingService()

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

    def run(self):
        while self.thermostat.isAlive:
            self.thermostat.update()

            status_string = 'Target T: {}, Current T: {}, Outside T: {}'.format(
                self.thermostat.targetTemp, self.thermostat.feedbackTemp, self.thermostat.ambientTemp)
            self.logger.info(status_string)

            self.logger.info('Boiler state: {}'.format(self.thermostat.boilerActive))

            now = int(time.time())
            self.databaseLoggingService.add_row_to_db(now,
                                                      self.thermostat.feedbackTemp, self.thermostat.targetTemp,
                                                      self.thermostat.ambientTemp, self.thermostat.boilerActive)
            time.sleep(REFRESH_PERIOD)

    def kill(self):
        self.telegram_updater.idle()
        self.thermostat.kill()
        sys.exit(0)
        pass

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hello!  This is your thermostat. Send /status for current info.  Send /set to change settings")

    def status(self, update, context):
        if self.thermostat.try_update_temperatures():
            message_text = 'Target T: {}, Current T: {}, Ambient T: {}, Boiler status: {}'.format(
                self.thermostat.targetTemp, self.thermostat.feedbackTemp,
                self.thermostat.ambientTemp, self.thermostat.boilerActive)

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=message_text)

    def set(self, update, context):
        try:
            # args[0] should contain the thing to change, args[1] the new value
            param = context.args[0]
            value = float(context.args[1])

            if param in ['morning_beginning', 'morning_end', 'evening_beginning', 'evening_end']:
                value = to_time(value)

            self.thermostat.set_parameter(param, value)

            update.message.reply_text('{} updated to {}'.format(param, value))

        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /set <night_temp/day_temp/away_temp, morning_beginning/morning_end/evening_beginning/evening_end>')

    def plot(self, update, context):
        now = int(time.time())
        yesterday = now - 3600 * 24

        times, sensor_temps, target_temps, boiler_ons = self.databaseLoggingService.select_data_in_range(yesterday, now)

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
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(file_handler)
        l.addHandler(stream_handler)
        return l


if __name__ == "__main__":
    print('Starting...')
    thermostatService = ThermostatService('config.yml')

    try:
        thermostatService.run()
    except KeyboardInterrupt:
        thermostatService.kill()
