import atexit
import datetime
import time
from requests.exceptions import ReadTimeout, ConnectionError
import teslapy

from optimiser.solar_charge_state import SolarChargeState


class TeslaAPI:

    def __init__(self, username: str, car_index: int = 0, battery_index: int = 0):
        """
        A wrapper for the Tesla API
        Args:
            username: The username to use to log in to Tesla
            car_index: The index in the list of vehicles output from the tesla api watched by this object
            battery_index: The index in the list of batteries output from the tesla api watched by this object
        """
        self.request_attempts = 50
        self.username = username
        self.car_index = car_index
        self.battery_index = battery_index
        self.tesla = None

    def connect(self):
        """ Connects to the API """

        register = True if self.tesla is None else False
        self.tesla = teslapy.Tesla(self.username)
        if register:  # Make sure to close the connection on exit
            atexit.register(self.tesla.close)

        # This will open the url to authenticate. The url from the page not found wilkl need to be copied
        # into this input to be able to extract the token
        if not self.tesla.authorized:
            print('Use browser to login. Page Not Found will be shown at success.')
            print('Open this URL: ' + self.tesla.authorization_url())
            self.tesla.fetch_token(authorization_response=input('Enter URL after authentication: '))

    def send_command(self, command: str, **kwargs):
        """
        Sends a command to the tesla api
        Args:
            command: The command to send
            **kwargs: Any additional parameters required with the command
        """

        # Keep trying to send the command until success or request_attempts has been reached
        counter = 0
        while counter < self.request_attempts:
            try:
                self.tesla.vehicle_list()[self.car_index].command(command, **kwargs)
                return
            except teslapy.HTTPError as e:
                self.tesla.vehicle_list()[self.car_index].sync_wake_up()
                print(f"\r{e}")
                time.sleep(2)
                counter += 1

    def update_solar_charge_state(self, solar_charge_state: SolarChargeState) -> SolarChargeState:
        """
        Takes an existing SolarChargeState and updates it with new information
        Args:
            solar_charge_state: The existing solar charge state to update

        Returns:
            The updated SolarChargeState
        """
        request_attempts = self.request_attempts

        while request_attempts >= 0:
            try:
                car_data = self.tesla.vehicle_list()[self.car_index].get_vehicle_data()
                battery_data = self.tesla.battery_list()[self.battery_index].get_battery_data()
            except (teslapy.HTTPError, ReadTimeout, ConnectionError) as e:
                self.tesla.vehicle_list()[self.car_index].sync_wake_up()
                # TODO: Fix this - the car does not report any data after it goes to sleep
                request_attempts -= 1
                continue

            power_data = battery_data.get('power_reading')[0]

            solar_charge_state.current_load = power_data['load_power']
            solar_charge_state.current_generation = power_data['solar_power']
            solar_charge_state.update_spare_capacity(
                timestamp=datetime.datetime.now().timestamp(),
                value=solar_charge_state.spare_capacity)
            solar_charge_state.charge_state = car_data['charge_state']['charging_state']
            solar_charge_state.charge_current_request = car_data['charge_state']['charge_current_request']
            solar_charge_state.vehicle_charge = car_data['charge_state']['battery_level']
            battery_perc = battery_data.get('energy_left') / battery_data.get('total_pack_energy') * 100
            solar_charge_state.battery_charge = battery_perc

            return solar_charge_state
        return solar_charge_state
