
from datetime import timedelta, datetime, date
import calendar

def all_dates_between_dates(check_in, check_out):

    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]

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
    if len(month)<1:
        month = '0'+ month
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


