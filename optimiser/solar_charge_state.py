from collections import deque
import datetime
from typing import Dict


class SolarChargeState:

    def __init__(
            self,
            current_load: int = 0,
            current_generation: int = 0,
            charge_state: str = 'Disconnected',
            charge_current_request: int = 0,
            vehicle_charge: float = 0,
            battery_charge: float = 0,
            history_count: int = 30,
            amps_per_kw: int = 5,
            max_amps: int = 10,
            time_format: str = '%d/%m/%Y %H:%M:%S'):
        """
        The model for solar charge state that combines info from the vehicle and the powerwall
        Args:
            current_load: The current usage of power from the household in W
            current_generation: The amount of power generated from solar in W
            charge_state: The current charging state of the vehicle e.g. Disconnected, Charging ect.
            charge_current_request: The number of amps set for charging power.
            vehicle_charge: The percentage of battery that is charged in the vehicle
            battery_charge: The percentage of battery that is charged for the powerwall
            history_count: The number of time periods to retain for calculating the moving average
            amps_per_kw: The factor to use to determine the current request for charging the vehicle
            max_amps: The max amps the current charger can output
            time_format: The format of the time for output
        """
        self.current_load = current_load
        self.current_generation = current_generation
        self.charge_state = charge_state
        self.charge_current_request = charge_current_request
        self.spare_capacity_history = deque()
        self.vehicle_charge = vehicle_charge
        self.battery_charge = battery_charge
        self.history_count = history_count
        self.amps_per_kw = amps_per_kw
        self.max_amps = max_amps
        self.time_format = time_format

    def __str__(self) -> str:
        return f"{f'{self._now}'.ljust(15)} | " \
               f"{f'State: {self.charge_state} '.ljust(15)} | " \
               f"{f'Load: {self.current_load / 1000: .2f} kW'.ljust(15)} | " \
               f"{f'Gen: {self.current_generation / 1000: .2f} kW'.ljust(15)} | " \
               f"{f'Spare Cap.: {self.spare_capacity / 1000: .2f} kW'.ljust(20)} | " \
               f"{f'Avg. Spare Cap.: {self.avg_spare_capacity / 1000:.2f} kW'.ljust(25)} | " \
               f"{f'Charge Rate: {self.charge_current_request} Amps'.ljust(20)} | " \
               f"{f'Vehicle: {self.vehicle_charge:.0f}%'.ljust(15)} | " \
               f"{f'Powerwall: {self.battery_charge:.0f}%'.ljust(15)} |"

    @property
    def json(self) -> Dict:
        """ Formats data in json """
        return {
            'last_updated': self._now,
            'charge_state': self.charge_state,
            'current_load': self.current_load,
            'current_generation': self.current_generation,
            'spare_capacity': self.spare_capacity,
            'charge_current_request': self.charge_current_request,
            'vehicle_charge': self.vehicle_charge,
            'battery_charge': self.battery_charge,
            'spare_capacity_history': list(self.spare_capacity_history)
        }

    @property
    def csv(self) -> str:
        """ Formats data in csv """
        return f"{self._now}," \
               f"{self.charge_state}," \
               f"{self.current_load}," \
               f"{self.current_generation}," \
               f"{self.spare_capacity}," \
               f"{self.charge_current_request}," \
               f"{self.vehicle_charge}," \
               f"{self.battery_charge}\n"

    @property
    def avg_spare_capacity(self) -> float:
        """ The moving average of spare capacity i.e. generation - load """
        if len(self.spare_capacity_history) > 0:
            return sum(item['value'] for item in self.spare_capacity_history) / len(self.spare_capacity_history)
        else:
            return 0

    @property
    def spare_capacity(self) -> int:
        """ The current spare capacity i.e. generation - load """
        return self.current_generation - self.current_load

    @property
    def possible_charge_current(self) -> int:
        """ Amount of current that can be used with the excess solar generation without consuming grid energy """
        return min(
            int(self.charge_current_request + (self.avg_spare_capacity / 1000 * self.amps_per_kw)),
            self.max_amps)

    @property
    def is_charge_change(self) -> bool:
        """ Flag to determine if the possible charge current is different from the current"""
        return self.possible_charge_current != self.charge_current_request

    @property
    def _now(self) -> str:
        """ The current time represented as a string """
        return datetime.datetime.now().strftime(self.time_format)

    def update_spare_capacity(self, timestamp: int, value: int):
        """
        Adds a value to the spare capacity history
        Args:
            timestamp: The timestamp of when the value occurred
            value: The value to add to the series
        """
        self.spare_capacity_history.append({'timestamp': timestamp, 'value': value})
        if len(self.spare_capacity_history) > self.history_count:
            self.spare_capacity_history.popleft()

