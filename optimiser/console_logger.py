from termcolor import colored


class ConsoleLogger:

    @staticmethod
    def log(message: str, severity: str = 'DEBUG'):
        """
        Logs a message to the console in different colours for different severity types
        Args:
            message: The message to log
            severity: The severity of the message which can determine the colour displayed
        """
        color = None
        if severity == 'DEBUG':
            color = 'blue'
        elif severity == 'ERROR':
            color = 'red'

        print(colored(message, color))
