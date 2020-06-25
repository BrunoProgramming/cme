import argparse
import pandas as pd
import numpy as np
import statistics
import tqdm
import re
from datetime import datetime
import mysql.connector as mysql

_pat_option_title = re.compile(r"([A-Z]{3} \d\d) (Calls|Puts)")
_ignored_strings = set(["Strike", "TOTALS", "Month", "No month data for this option type"])

def main(args):
    report_date = datetime.strptime(args.date, '%Y%m%d')
    product = args.product
    print("Process {} {} {}".format(args.input, product, report_date))
    df = pd.read_excel(args.input, skiprows=0)
    #print (df.info())
    #print (df)
    calls = {}
    puts = {}
    skip = False
    for index, row in df.iterrows():
        key = str(row[0])
        if not key or key == "nan" or key.startswith("OPTION TYPE: "):
            skip = False
            continue
        elif skip:
            continue
        elif key == "Futures":
            skip = True
            continue

        match = _pat_option_title.match(key)
        if match:
            exercise_date = convert_execise_date(match.group(1))
            print(exercise_date)
            direction = match.group(2)
            if direction!='Calls' and direction!='Puts':
                raise ValueError('"{}" should contains Calls or Puts'.format(key))
            is_call = 1 if direction=='Calls' else 0
            dct = calls if is_call else puts
            if not dct.get(exercise_date):
                dct[exercise_date] = {}
            dct = dct[exercise_date]
        elif key.lstrip('-+').isnumeric():
            strike = atoi(key)
            at_close = atoi(row[8])
            dct[strike] = dct.get(strike, 0) + at_close
            #if at_close>5000:
            #    print(exercise_date, direction, key, at_close)
        else:
            if key and key not in _ignored_strings:
                raise ValueError('key is not valid "{}"'.format(key))

    db = mysql.connect(
            host = "localhost",
            user = "xicen",
            passwd = "111111",
            database = "options"
            )
    cursor = db.cursor()
    query_base = "INSERT INTO options_{} (IsCall, ExerciseDate, Strike, Date, AtClose) VALUES ".format(product)
    for exercise_date, dct in calls.items():
        query = '{}(1, "{}", %s, "{}", %s);'.format(query_base, exercise_date.strftime("%Y-%m-%d"), report_date.strftime("%Y-%m-%d"))
        print(query)
        cursor.executemany(query, dct.items())
    for exercise_date, dct in puts.items():
        query = '{}(0, "{}", %s, "{}", %s);'.format(query_base, exercise_date.strftime("%Y-%m-%d"), report_date.strftime("%Y-%m-%d"))
        print(query)
        cursor.executemany(query, dct.items())
    db.commit()
    print(cursor.rowcount, "records inserted")
    

def atoi(s):
    return int(s.replace(',', ''))


def convert_execise_date(execise_date):
    month, year = execise_date.split(' ')

    table = {"JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12}

    date = datetime(month=table.get(month), day=1, year=2000+int(year))
    print('Parse {} to {}'.format(execise_date, date))
    return date


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Option Analysis")
    parser.add_argument("--input", type=str, help="input excel")
    parser.add_argument("--date", type=str, help="report date")
    parser.add_argument("--product", type=str, help="option product")
    args = parser.parse_args()

    main(args)
