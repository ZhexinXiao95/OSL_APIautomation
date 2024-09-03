import os
import datetime

class Logger:
    COLOR_RESET = "\033[0m"
    COLOR_RED = "\033[91m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_MAGENTA = "\033[95m"  # 品红色

    def __init__(self):
        self.log_file_name = self._generate_log_file_name()
        self._ensure_log_file_exists()

    def log(self, message, level='info'):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color_prefix = {
            'info': '',
            'warning': self.COLOR_YELLOW,
            'error': self.COLOR_RED,
            'debug': self.COLOR_BLUE,
            'critical': self.COLOR_MAGENTA
        }.get(level.lower(), self.COLOR_GREEN)

        log_message = f"[{timestamp}] [{level.upper()}] {message}"

        self._write_to_file(log_message)

        # Output the message with the appropriate color
        print(f"{color_prefix}{log_message}{self.COLOR_RESET}")

    def _write_to_file(self, message):
        with open(self.log_file_name, 'a') as log_file:
            log_file.write(message + '\n')

    def _generate_log_file_name(self):
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')  # 上级目录的 logs 文件夹
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        today = datetime.date.today()
        return os.path.join(logs_dir, f"log_{today.strftime('%Y-%m-%d')}.log")

    def _ensure_log_file_exists(self):
        if not os.path.exists(self.log_file_name):
            with open(self.log_file_name, 'w') as log_file:
                log_file.write("Log file created.\n")

logger = Logger()
if __name__ == '__main__':
    # Example usage
    logger.log("This is an informational message", 'info')
    logger.log("This is a warning message", 'warning')
    logger.log("This is an error message", 'error')
    logger.log("This is a debug message", 'debug')
    logger.log("This is a critical message", 'critical')


