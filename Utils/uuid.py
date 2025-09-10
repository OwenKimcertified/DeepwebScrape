import time
import threading

class SnowflakeGenerator:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _current_timestamp(self):
        # Twitter 기준 epoch: 1288834974657
        return int(time.time() * 1000) - 1288834974657

    def generate_id(self):
        with self.lock:
            timestamp = self._current_timestamp()

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._current_timestamp()
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            snowflake_id = ((timestamp & 0x1FFFFFFFFFF) << 22) | (self.machine_id << 12) | self.sequence
            return snowflake_id
