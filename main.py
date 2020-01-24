from Services.ThermostatService import ThermostatService

thermostatService = ThermostatService('config.yml')

try:
    thermostatService.run()
except KeyboardInterrupt:
    thermostatService.kill()
