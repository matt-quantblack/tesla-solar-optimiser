import datetime
import json
import time
from pathlib import Path
from typing import Any

import teslapy
from termcolor import colored
from optimiser.solar_charge_state import SolarChargeState


class TeslaSolarOptimiser:

    def __init__(
            self,
            tesla_api: Any,
            new_command_interval: int = 120,
            car_index: int = 0,
            battery_index: int = 0,
            data_logger: Any = None):
        """
        The optimiser that fetches state data and makes decisions on whether to charge the car.
        Args:
            tesla_api: Any api object that satisfies the interface
            new_command_interval: The time in seconds to wait between sending commands to avoid sending too many at once
            car_index: The index in the list of vehicles output from the tesla api watched by this object
            battery_index: The index in the list of batteries output from the tesla api watched by this object
            data_logger: Any logger object that satisfies the interface
        """
        self.tesla_api = tesla_api
        self.new_command_interval = new_command_interval
        self.solar_charge_state = SolarChargeState()
        self.car_index = car_index
        self.battery_index = battery_index
        self.last_command_time = None
        self._loggers = []
        self.data_logger = data_logger

    def connect(self):
        """ Connects to the API """
        self.tesla_api.connect()

    def run(self):
        """
        The main run loop that displays charge state and makes decisions on weather to charge the vehicle
        """
        while True:
            self.solar_charge_state = self.tesla_api.update_solar_charge_state(
                solar_charge_state=self.solar_charge_state)
            Path('current_state.json').write_text(json.dumps(self.solar_charge_state.json))
            if self.solar_charge_state is not None:
                self._display_console(str(self.solar_charge_state))
                self._determine_command()
                self._log_data()
            time.sleep(10)

    def attach_logger(self, logger: Any):
        """
        Attaches a logger to print out messages
        Args:
            logger: Any logger object that satisfies the interface
        """
        self._loggers.append(logger)

    @property
    def secs_since_last_command(self) -> int:
        """ Returns the number of seconds since the last command was issued """
        if self.last_command_time is None:
            return None

        return (datetime.datetime.now() - self.last_command_time).total_seconds()

    @property
    def commands_allowed(self) -> bool:
        """ Returns true if a command can be issued """
        return self.last_command_time is None or self.secs_since_last_command > self.new_command_interval

    def _log_data(self):
        """ Logs the current charge state as a line of csv """
        if self.data_logger is not None:
            self.data_logger.log(self.solar_charge_state.csv)

    def _display_console(self, message: str):
        """
        Display the message in the console
        Args:
            message: The message to display
        """
        color = None
        if self.solar_charge_state.charge_state == 'Charging':
            color = 'green'
        if self.solar_charge_state.charge_state == 'Disconnected':
            color = 'red'
        print(colored(message, color))

    def _send_command(self, command: str, message: str = None, severity: str = 'DEBUG', **kwargs):
        """
        Sends a command to the api
        Args:
            command: The command to send
            message: A message to log otherwise logs the command if none
            severity: The severity of the log message
        """
        if self.commands_allowed:
            self.last_command_time = datetime.datetime.now()
            self.tesla_api.send_command(command, **kwargs)
            for logger in self._loggers:
                if message is not None:
                    logger.log(message, severity)
                else:
                    logger.log(command, severity)

    def _determine_command(self):
        """ Logic to determine if a command to start charging the car should be sent. """

        # Check if we have enough excess solar to start charging
        if self.solar_charge_state.avg_spare_capacity > 1250:
            if self.solar_charge_state.charge_state == 'Stopped':
                self._send_command('START_CHARGE')
                self.solar_charge_state.charge_current_request = 0
                self._send_command(
                    'CHARGING_AMPS',
                    message=f'Setting CHARGING AMPS to {self.solar_charge_state.possible_charge_current}',
                    charging_amps=self.solar_charge_state.possible_charge_current)

        # Check if we should increase or decrease the charge current or stop charging all together
        if self.solar_charge_state.charge_state == 'Charging':
            if self.solar_charge_state.avg_spare_capacity < 0:
                # Stop charging because we don't have enough to even run a minimum charge
                if self.solar_charge_state.possible_charge_current < 5:
                    self._send_command('STOP_CHARGE')
                elif self.solar_charge_state.is_charge_change:
                    self._send_command(
                        'CHARGING_AMPS',
                        message=f'Setting CHARGING AMPS to {self.solar_charge_state.possible_charge_current}',
                        charging_amps=self.solar_charge_state.possible_charge_current)
            else:
                if self.solar_charge_state.is_charge_change:
                    self._send_command(
                        'CHARGING_AMPS',
                        message=f'Setting CHARGING AMPS to {self.solar_charge_state.possible_charge_current}',
                        charging_amps=self.solar_charge_state.possible_charge_current)





