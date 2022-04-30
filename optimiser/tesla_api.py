import atexit
import datetime
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
        self.request_attempts = 2
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

        try:
            self.connect()
            self.tesla.vehicle_list()[self.car_index].sync_wake_up()
            self.tesla.vehicle_list()[self.car_index].command(command, **kwargs)
            return "Command Success", True
        except (teslapy.HTTPError, teslapy.VehicleError) as e:
            return f"{e}", False

    def update_car_charge_state(self, solar_charge_state: SolarChargeState) -> SolarChargeState:
        """
        Takes an existing SolarChargeState and updates it with new information from the car
        Args:
            solar_charge_state: The existing solar charge state to update

        Returns:
            The updated SolarChargeState
        """
        request_attempts = self.request_attempts
        car_data = None

        while car_data is None:
            try:
                self.connect()
                self.tesla.vehicle_list()[self.car_index].sync_wake_up()
                car_data = self.tesla.vehicle_list()[self.car_index].get_vehicle_data()
            except (teslapy.HTTPError, ReadTimeout, ConnectionError, teslapy.VehicleError) as e:
                request_attempts -= 1
                if request_attempts == 0:
                    raise ConnectionError(f"Could not connect to car: {e}")

        solar_charge_state.charge_state = car_data['charge_state']['charging_state']
        solar_charge_state.charge_current_request = car_data['charge_state']['charge_current_request']
        solar_charge_state.vehicle_charge = car_data['charge_state']['battery_level']
        solar_charge_state.port_open = car_data['charge_state']['charge_port_door_open']

        return solar_charge_state

    def update_battery_charge_state(self, solar_charge_state: SolarChargeState) -> SolarChargeState:
        """
        Takes an existing SolarChargeState and updates it with new information from the battery
        Args:
            solar_charge_state: The existing solar charge state to update

        Returns:
            The updated SolarChargeState
        """
        request_attempts = self.request_attempts
        battery_data = None

        while battery_data is None:
            try:
                battery_data = self.tesla.battery_list()[self.battery_index].get_battery_data()
            except (teslapy.HTTPError, ReadTimeout, ConnectionError) as e:
                request_attempts -= 1
                if request_attempts == 0:
                    raise ConnectionError(f"Could not connect to battery: {e}")

        power_data = battery_data.get('power_reading')[0]

        solar_charge_state.current_load = power_data['load_power']
        solar_charge_state.current_generation = power_data['solar_power']
        solar_charge_state.update_spare_capacity(
            timestamp=datetime.datetime.now().timestamp(),
            value=solar_charge_state.spare_capacity)
        battery_perc = battery_data.get('energy_left') / battery_data.get('total_pack_energy') * 100
        solar_charge_state.battery_charge = battery_perc

        return solar_charge_state
