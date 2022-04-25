import datetime
import json
import time
from pathlib import Path
from typing import Any
from optimiser.force_charge_command import ForceChargeCommand
from optimiser.solar_charge_state import SolarChargeState
from requests.exceptions import ConnectionError


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
        loop_counter = 0
        while True:
            try:
                self.solar_charge_state = self.tesla_api.update_battery_charge_state(
                    solar_charge_state=self.solar_charge_state)
            except ConnectionError as e:
                self._log(str(e), severity='ERROR')

            # Only update the car data every 60 loops to minimise car awake time
            if loop_counter % 40 == 0:
                try:
                    self.solar_charge_state = self.tesla_api.update_car_charge_state(
                        solar_charge_state=self.solar_charge_state)
                    self._log("Car data updated.", severity='DEBUG')
                except ConnectionError as e:
                    self._log(str(e), severity='ERROR')

            Path('current_state.json').write_text(json.dumps(self.solar_charge_state.json))
            if self.solar_charge_state is not None:
                self._log(
                    message=str(self.solar_charge_state),
                    severity=self._get_message_severity(self.solar_charge_state.charge_state))
                self._log_data()
                self._determine_command()

            loop_counter += 1

            time.sleep(20)

    def attach_logger(self, logger: Any):
        """
        Attaches a logger to print out messages
        Args:
            logger: Any logger object that satisfies the interface
        """
        self._loggers.append(logger)

    def _log(self, message: str, severity: str = 'DEBUG'):
        """
        Sends the log message to all loggers

        Args:
            message: The message to log
            severity: The severity of the message
        """
        for logger in self._loggers:
            if message is not None:
                logger.log(message, severity)
            else:
                logger.log(message, severity)

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

    @staticmethod
    def _get_message_severity(charge_state: str) -> str:
        """ Gets a colour based on charge state.
        Args:
            charge_state: The current charging state
            """
        severity = 'DEBUG'
        if charge_state == 'Charging':
            severity = 'SUCCESS'
        if charge_state == 'Disconnected':
            severity = 'ERROR'
        return severity

    def _send_command(self, command: str, message: str = None, severity: str = 'DEBUG', force_command=False, **kwargs):
        """
        Sends a command to the api
        Args:
            command: The command to send
            message: A message to log otherwise logs the command if none
            severity: The severity of the log message
            force_command: If True bypasses the commands allowed check
        """
        if self.commands_allowed or force_command:
            self.last_command_time = datetime.datetime.now()
            result, success = self.tesla_api.send_command(command, **kwargs)
            if success:
                self._log(message, severity) if message is not None else self._log(command, severity)
            else:
                self._log(result, severity="ERROR")

            # Update the car data
            try:
                self.solar_charge_state = self.tesla_api.update_car_charge_state(
                    solar_charge_state=self.solar_charge_state)
                self._log("Car data updated.", severity='DEBUG')
            except ConnectionError as e:
                self._log(str(e), severity='ERROR')

    def _determine_command(self):
        """ Logic to determine if a command to start charging the car should be sent. """

        # Load any force charge commands
        force_charge_command: ForceChargeCommand = ForceChargeCommand.load()
        now = datetime.datetime.now()

        if self.solar_charge_state.charge_state == "Complete" and self.solar_charge_state.port_open is False:
            self._send_command('CHARGE_PORT_DOOR_OPEN')  # Unlock the charge port

        # Check if we have enough excess solar to start charging or if we are force charging car
        elif self.solar_charge_state.avg_spare_capacity > force_charge_command.min_spare_capacity \
                or self.solar_charge_state.vehicle_charge < force_charge_command.min_vehicle_charge \
                or force_charge_command.force_charge is True:
            if self.solar_charge_state.charge_state == 'Stopped':
                self._send_command('START_CHARGE')

                # If we are below the minimum charge then force charge for 'force_charge_hours'
                if self.solar_charge_state.vehicle_charge < force_charge_command.min_vehicle_charge:
                    self._log(
                        f'Battery charge below minimum of {force_charge_command.min_vehicle_charge}',
                        severity='INFO')
                # If we are below the minimum charge then force charge for 'force_charge_hours'
                if force_charge_command.force_charge:
                    self._log(
                        f'Force charge activated',
                        severity='INFO')

                # If this was force charged then record the start time
                if self.solar_charge_state.avg_spare_capacity <= force_charge_command.min_spare_capacity:
                    force_charge_command.request_time = now
                    force_charge_command.save()

        # Check if we should increase or decrease the charge current or stop charging all together
        if self.solar_charge_state.charge_state == 'Charging':
            new_charging_amps = 0

            # Stop charging because we don't have enough to even run a minimum charge but only if not force charging
            if self.solar_charge_state.avg_spare_capacity < 0:
                is_forcing = force_charge_command.is_forcing_charge(
                    self.solar_charge_state.vehicle_charge)
                self._log(f"Low Capacity; "
                          f""
                          f"Possible charge rate: "
                          f"{self.solar_charge_state.possible_charge_current}, "
                          f"Is forcing: {is_forcing}")

                if self.solar_charge_state.possible_charge_current < 5 and \
                        not is_forcing:
                    self._send_command('STOP_CHARGE')
                    self._send_command('CHARGE_PORT_DOOR_OPEN')  # Unlock the charge port

                    # Mark force charging as complete since is_forcing_charge returns False - meaning it completed.
                    if force_charge_command.request_time is not None:
                        force_charge_command.request_time = None
                        force_charge_command.save()

                    return

            # Otherwise, see if we can increase the charge if the possible charge is different to current
            if self.solar_charge_state.is_charge_change:
                if self.solar_charge_state.vehicle_charge < force_charge_command.min_vehicle_charge:
                    new_charging_amps = force_charge_command.force_charge_amps
                else:
                    new_charging_amps = self.solar_charge_state.possible_charge_current

            # A change in charging amps is required
            if new_charging_amps > 0:
                self._send_command(
                    'CHARGING_AMPS',
                    message=f'Setting CHARGING AMPS to {new_charging_amps}',
                    charging_amps=new_charging_amps)
