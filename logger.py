from pathlib import Path

def log(message):
    """Log messages to file."""
    print(message)
    log_file = Path('./data/log.txt')
    with open(log_file, "a+") as file:
        file.write(f"{message}\n")
