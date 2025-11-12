from datetime import datetime
from datetime import timedelta

def get_time():
    return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    target_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M:%S")
    while get_time() != target_time:
        pass
    print("Time to wake up!")
