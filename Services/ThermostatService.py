import datetime
import os
import sys
import time
import uuid
import matplotlib
import matplotlib.pyplot as plt
from telegram.ext import Updater, CommandHandler, Filters
from utils import to_time, read_config, setup_logger
from Models.Thermostat import Thermostat
from Services.DatabaseServices import ThermostatDatabaseService
from Services.HouseModelFittingService import HouseModelFittingService

matplotlib.use("Agg")

REFRESH_PERIOD = 30


class ThermostatService:
    def __init__(self, configuration_file):

        self.parameter_names = ['morning_beginning', 'morning_end',
                                'evening_beginning', 'evening_end',
                                'night_temp', 'day_temp', 'away_temp']

        self.logger = setup_logger('Thermostat.log')

        self.thermostat_database_service = ThermostatDatabaseService(False)
        self.house_model_fitting_service = HouseModelFittingService()

        config = read_config(configuration_file)
        if config:
            self.thermostat = Thermostat(config)

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

            get_handler = CommandHandler('get', self.get, pass_args=True)
            self.telegram_dispatcher.add_handler(get_handler)

            plot_handler = CommandHandler('plot', self.plot)
            self.telegram_dispatcher.add_handler(plot_handler)

            self.telegram_updater.start_polling()
        else:
            raise Exception("Unable to load thermostat config")

    def run(self):
        while self.thermostat.is_alive:
            self.thermostat.update()
            self.logger.info(self._thermostat_status_string())

            if self.thermostat.boiler_changed_state:
                house_model = self.house_model_fitting_service.fit_house_model(self.thermostat.boiler_active)
                if house_model:
                    self.thermostat.set_parameter('house_model', house_model)

            now = int(time.time())
            self.thermostat_database_service.add_row_to_db(now,
                                                           self.thermostat.feedback_temp, self.thermostat.target_temp,
                                                           self.thermostat.ambient_temp, self.thermostat.boiler_active)
            time.sleep(REFRESH_PERIOD)

    def kill(self):
        self.telegram_updater.idle()
        self.thermostat.kill()
        sys.exit(0)

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hello!  This is your thermostat. Send /status for current info.  Send /set to change settings")

    def status(self, update, context):
        if self.thermostat.try_update_temperatures():
            message_text = self._thermostat_status_string()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=message_text)

    def get(self, update, context):
        try:
            if len(context.args) > 0:
                param = context.args[0]
                if param in self.parameter_names:
                    value = self.thermostat.get_parameter(param)
                    params = [param]
                    values = [value]
            else:
                params = self.parameter_names
                values = []
                for param in params:
                    values.append(self.thermostat.get_parameter(param))

            message = ''
            for (param, value) in zip(params, values):
                message += '{} = {}\n'.format(param, value)

            context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /get <night_temp/day_temp/away_temp, morning_beginning/morning_end/evening_beginning/evening_end>')

    def set(self, update, context):
        try:
            # args[0] should contain the thing to change, args[1] the new value
            param = context.args[0]
            value = float(context.args[1])

            if param in ['morning_beginning', 'morning_end', 'evening_beginning', 'evening_end']:
                value = to_time(value)

            if param in self.parameter_names:
                self.thermostat.set_parameter(param, value)
                update.message.reply_text('{} updated to {}'.format(param, value))
            else:
                update.message.reply_text('Invalid parameter')
                context.args = []
                self.get(update, context)

        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /set <night_temp/day_temp/away_temp, morning_beginning/morning_end/evening_beginning/evening_end>')

    def plot(self, update, context):
        now = int(time.time())
        yesterday = now - 3600 * 24

        times, sensor_temps, target_temps, boiler_ons, _ = self.thermostat_database_service.select_data_in_range(
            yesterday,
            now)

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

    def _thermostat_status_string(self):
        return 'Target T: {}, Current T: {}, Ambient T: {}, Boiler status: {}'.format(
            self.thermostat.target_temp, self.thermostat.feedback_temp,
            self.thermostat.ambient_temp, self.thermostat.boiler_active)
