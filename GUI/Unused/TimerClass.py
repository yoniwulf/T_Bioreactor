import time


class ProfileTimer:
    def __init__(self, hours=0, minutes=0, seconds=0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.total_time = self.hours * 3600 + self.minutes * 60 + self.seconds
        self.remaining_time = self.total_time
        self.paused = False

    def setTime(self, hours=0, minutes=0, seconds=0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.total_time = self.hours * 3600 + self.minutes * 60 + self.seconds
        self.remaining_time = self.total_time

    def start(self):
        while self.remaining_time > 0:
            if not self.paused:
                self.remaining_time -= 1
                time.sleep(1)
                self.print_time()
            else:
                time.sleep(1)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self.start()

    def reset(self):
        self.remaining_time = self.total_time

    def print_time(self):
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
