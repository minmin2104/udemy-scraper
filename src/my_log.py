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
        print(message, end=end)
        with open(path, 'a') as f:
            f.write(f'{message}{end}')

    def log_time(self, _func):
        def func():
            start_time = datetime.now()
            _func()
            end_time = datetime.now()

            elapsed = end_time - start_time
            self.log(f"Elapsed time: {elapsed}")
            self.log(f"Total second: {elapsed.total_seconds()}")
        return func
