from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class ColorLogger:
    def __init__(self, name="Logger"):
        self.name = name

    def log(self, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{timestamp}] {self.name}: {message}{Style.RESET_ALL}")

    def info(self, message): self.log(message, color=Fore.CYAN)
    def success(self, message): self.log(message, color=Fore.GREEN)
    def warning(self, message): self.log(message, color=Fore.YELLOW)
    def error(self, message): self.log(message, color=Fore.RED)
    def debug(self, message): self.log(message, color=Fore.MAGENTA)

