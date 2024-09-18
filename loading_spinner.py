import itertools
import sys
import time

spinner_chars = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]

def loading_spinner(duration, message="Generating calendar file... Please wait."):
    spinner = itertools.cycle(spinner_chars)
    end_time = time.time() + duration

    sys.stdout.write(f"{message}")
    sys.stdout.flush()

    while time.time() < end_time:
        sys.stdout.write(f'\r\033[92m{next(spinner)} {message} \033[0m')
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write(f'\r')

    sys.stdout.write(f'\r{message} Done.\n')
    sys.stdout.flush()