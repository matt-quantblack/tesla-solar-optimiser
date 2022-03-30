import datetime


class LocalFileLogger:

    def __init__(self, filepath: str, error_filepath: str = None, include_timestamp: bool = True):
        """
        Logs messages to files
        Args:
            filepath: The default filepath to log messages
            error_filepath: The filepath to log ERROR severity messages
            include_timestamp: boolean to determine if the timestamp should be prepended to each message
        """
        self.filepath = filepath
        self.include_timestamp = include_timestamp
        if error_filepath is None:
            self.error_filepath = filepath
        else:
            self.error_filepath = error_filepath

    def log(self, message: str, severity: str = 'DEBUG'):
        """
        Logs messages to a log file and ERROR messages to an errors log file
        Args:
            message: The message to log
            severity: The severity of the message. ERROR will log to error filepath
        """

        if severity == 'ERROR':
            filepath = self.error_filepath
        else:
            filepath = self.filepath

        with open(filepath, "a") as log_file:
            if self.include_timestamp:
                line = f"{datetime.datetime.now()}: {message}\n"
            else:
                line = message
            log_file.write(line)
