from datetime import date, datetime, time
from babel.dates import format_date, format_datetime, format_time

#MM-DD-YYYY
def convertDate(dateIn : str) -> str:
    print(dateIn)
    return format_date(date(int(dateIn[6:10]), int(dateIn[0:2]), int(dateIn[3:5])), locale='en')
