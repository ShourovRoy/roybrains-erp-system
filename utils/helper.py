from datetime import datetime

def encode_date_time(date_time):
    return datetime.strptime(date_time, "%Y-%m-%dT%H:%M")