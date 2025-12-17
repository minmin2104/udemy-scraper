import os
from datetime import datetime


class MyLog:
    BASE_DIR = 'logs'
    BASE_FILENAME = 'log_'

    def __init__(self):
        dt = datetime.now()
        self.now = dt.strftime('%d-%b-%Y-%H-%M-%S')

    def log(self, message, end='\n'):
        filename = f'{self.BASE_FILENAME}{self.now}.txt'
        path = f'{self.BASE_DIR}/{filename}'
        if not os.path.exists(self.BASE_DIR):
            os.makedirs(self.BASE_DIR, exist_ok=True)
        with open(path, 'a') as f:
            f.write(f'{message}{end}')
