import datetime as dt
# модуль добавляет в футер текущий год, это было 
# одним из заданий в теории, решил оставить


def footer(request):
    d = dt.datetime.now().date()
    year = d.year
    return {'year':year,}