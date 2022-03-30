import argparse
from optimiser.tesla_api import TeslaAPI
from optimiser.tesla_solar_optimiser import TeslaSolarOptimiser
from optimiser.console_logger import ConsoleLogger
from optimiser.local_file_logger import LocalFileLogger


if __name__ == "__main__":
    """
    The optimiser app that interacts with the Tesla API, gets current state and makes a decision to charge the
    car, including the charge power.
    The optimiser takes in a tesla api object and several loggers for logging data and messages.
    """
    parser = argparse.ArgumentParser(description='Boot the TSO servers')
    parser.add_argument('username', type=str,
                        help='The username used for the Tesla API')
    args = parser.parse_args()

    # The data logger logs the state to a csv file
    data_logger = LocalFileLogger('data.csv', include_timestamp=False)
    tso = TeslaSolarOptimiser(
        tesla_api=TeslaAPI(username=args.username),
        data_logger=data_logger)

    # Also log messages to the console and a file output
    tso.attach_logger(ConsoleLogger())
    tso.attach_logger(LocalFileLogger('log.txt', 'errors.txt'))

    # Connect the api and run the loop to check status and make decisions
    tso.connect()
    tso.run()
