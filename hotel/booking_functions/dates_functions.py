
from datetime import timedelta, datetime, date
import calendar

"""
now all dates between dates return all dates between daten even the two dates provides are 
in different month.

**** not tested between two different YEARS *****
"""
def all_dates_between_dates(uno:str, dos:str):
    print(uno,'holaaaaaaaa')
    uno = str(uno)[0:10]
    uno = datetime.strptime(uno, "%Y-%m-%d")
    dos = str(dos)[0:10]
    dos = datetime.strptime(dos, "%Y-%m-%d")


    if uno.month != dos.month:
        first_day_str = first_day_month_x(str(dos.month))
        first_day = datetime.strptime(first_day_str, "%Y-%m-%d")
        date_list = [(first_day + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((dos.day - first_day.day) + 1)]
        last_day_str = last_day_month_x(str(uno.month))
        last_day = datetime.strptime(last_day_str, "%Y-%m-%d")
        date_list2 = [(uno + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((last_day.day - uno.day) + 1)]
        res = date_list + date_list2

        return sorted(res)

    else:
        date_list = [(uno + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((dos.day - uno.day) + 1)]

        return date_list


def list_days_month():
    string_date = datetime.today()
    actual_day = string_date.day-1
    start_month = string_date - timedelta(actual_day)
    res = calendar.monthrange(string_date.year, string_date.month)[1]
    end_month = start_month + timedelta(res-1)
    lis_of_dates = all_dates_between_dates(start_month, end_month)

    return lis_of_dates

def first_day_month():
    string_date = date.today()
    actual_day = string_date.day-1
    start_month = str(string_date - timedelta(actual_day))
    start_month = datetime.strptime(start_month, '%Y-%m-%d')
    return start_month

def last_day_month():
    string_date = date.today()
    actual_day = string_date.day-1
    start_month = string_date - timedelta(actual_day)
    res = calendar.monthrange(string_date.year, string_date.month)[1]
    end_month = str(start_month + timedelta(res-1))
    end_month = datetime.strptime(end_month, '%Y-%m-%d')
    return end_month

def first_day_month_x(month:str): #format '02'
    string_date = date.today()
    year = string_date.strftime('%Y')
    if len(month) < 2:
        month = '0' + month
        fecha = year + '-' + month + '-01'
        return fecha
    else:
        fecha = year + '-' + month + '-01'
        return fecha



def last_day_month_x(month: str):#format '02'
    string_date = date.today()
    res = calendar.monthrange(string_date.year, int(month))[1]
    if len(month)<1:
        month = '0' + month
        end_month = str(string_date.year) + '-' + month + '-' + str(res)
        """end_month = datetime.strptime(end_month, '%Y-%m-%d')"""
        return end_month
    else:
        end_month = str(string_date.year) + '-' + month + '-' + str(res)
        """end_month = datetime.strptime(end_month, '%Y-%m-%d')"""
        return end_month


