import datetime as dt
# Tage pro Monat
tage_je_monat = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}

def datum_jahreshauptversammlung(jahr: int) -> dt.datetime:
    # find date for the annual general meeting (last saturday in january)
    for d in [31,30,29,28]:
        try:
            last_day = dt.datetime(year=jahr, month=1, day=d)
            break
        except:
            print(d)
            continue

    offset = (last_day.weekday() - 5)%7
    
    return last_day - dt.timedelta(days=offset)
