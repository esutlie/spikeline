import time


class Timer:
    def __init__(self):
        self.tic = time.time()

    def start(self):
        self.tic = time.time()

    def log(self, message=''):
        total = time.time() - self.tic
        print(f'{total:.2f} seconds for {message}')
        self.tic = time.time()
