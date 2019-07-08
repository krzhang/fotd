from colorama import Fore, Back, Style

class Colors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  # ENDC = '\033[0m'
  ENDC = Style.RESET_ALL
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  # mine below
  BLUE = Fore.BLUE
  YELLOW = Fore.YELLOW
  RED = Fore.RED
  GREEN = Fore.GREEN
  MAGENTA = Fore.MAGENTA
  CYAN = Fore.CYAN
  # RPS
  WIN = OKGREEN
  LOSE = Fore.RED
  INVERT = Fore.BLACK + Back.WHITE

