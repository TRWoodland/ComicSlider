import logging
from datetime import datetime


class CS_Logfile:
    def __init__(self, message=""):
        self.message = message
        self.today = datetime.today()
        self.logger_file = self.today.strftime("CS Logfile %d %B %Y")  # Today's date

        logging.basicConfig(filename=self.logger_file, level=logging.ERROR)

        # Python 3.9
        # logging.basicConfig(filename=self.logger_file, encoding='utf-8', level=logging.ERROR)

    def update(self):
        self.today = datetime.today()  # updates the time
        right_now = self.today.strftime("%H-%M-%S %d.%B.%Y: ")
        return right_now

    def log_info(self, message):
        logging.info(self.update() + str(message))

    def log_error(self, message):
        logging.error(self.update() + str(message))

    def log_warning(self, message):
        logging.warning(self.update() + str(message))
