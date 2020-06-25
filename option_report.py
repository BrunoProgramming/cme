import argparse
import pandas as pd
import numpy as np
import statistics
import tqdm
import re
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib
import mysql.connector as mysql


def main(args):
    report_date = datetime.strptime(args.date, '%Y%m%d')
    product = args.product
    curr_price = int(args.price)
    print("Process {} {}".format(product, report_date))

    db = mysql.connect(
            host = "localhost",
            user = "xicen",
            passwd = "111111",
            database = "options"
            )

    cursor = db.cursor()
    report_weekday = report_date.weekday()
    report_date_start =  report_date-timedelta(days=5 if report_weekday==4 else (6 if report_weekday==5 or report_weekday==3 else 7))
    query = "SELECT IsCall, ExerciseDate, Date, Strike, AtClose FROM options_{} WHERE Date>'{}' AND Date<='{}' ORDER BY ExerciseDate ASC, IsCall DESC, Date ASC, Strike ASC".format(product, report_date_start.strftime("%Y-%m-%d"), report_date.strftime("%Y-%m-%d"))
    cursor.execute(query)
    records = cursor.fetchall()
    data = []
    prev_exercise_date = None
    prev_is_call = None
    for row in records:
        is_call = row[0]
        exercise_date = row[1]
        date = row[2] #datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        strike = row[3]
        at_close = row[4]
        if exercise_date != prev_exercise_date or is_call != prev_is_call:
            if prev_exercise_date:
                if prev_date:
                    date_list.append((prev_date, strike_list))
                prev_date = date
                strike_list = []
                data.append((prev_exercise_date, prev_is_call, date_list, strike_set))
            prev_exercise_date = exercise_date
            prev_is_call = is_call
            date_list = []
            strike_set = set()
            prev_date = None
        if date != prev_date:
            if prev_date:
                date_list.append((prev_date, strike_list))
            prev_date = date
            strike_list = []
        strike_list.append((strike, at_close))
        strike_set.add(strike)
    if prev_exercise_date:
        if prev_date:
            date_list.append((prev_date, strike_list))
        data.append((prev_exercise_date, prev_is_call, date_list, strike_set))

    volumes = []
    for exercise_date, is_call, date_list, strike_set in data:
        print(exercise_date,date_list)
        strike_list_latest, strike_list_earlier = (), ()
        date, strike_list = date_list[-1]
        if date > report_date-timedelta(days=1):
            strike_list_latest = strike_list
        elif date > report_date-timedelta(days=2):
            strike_list_earlier = strike_list
        if len(date_list)>=2:
            date, strike_list = date_list[-2]
            if date > report_date-timedelta(days=1):
                strike_list_latest = strike_list
            elif date > report_date-timedelta(days=2):
                strike_list_earlier = strike_list
        change = 0
        change_above = 0
        for strike, at_close in strike_list_latest:
            change += at_close
            if is_call and strike > curr_price or not is_call and strike < curr_price:
                change_above += at_close
        for strike, at_close in strike_list_earlier:
            change -= at_close
            if is_call and strike > curr_price or not is_call and strike < curr_price:
                change_above -= at_close
        volumes.append([exercise_date, is_call, change, change_above])

    volumes_aggr = []
    volume_call_put = [0, 0]
    volume_call_put_above = [0, 0]
    for exercise_date, is_call, change, change_above in volumes:
        if not volumes_aggr:
            volumes_aggr.append([exercise_date, abs(change)])
        elif volumes_aggr[-1][0] == exercise_date:
            volumes_aggr[-1][1] += abs(change)
        else:
            volumes_aggr.append([exercise_date, abs(change)])
        volume_call_put[1 if is_call else 0] += change
        volume_call_put_above[1 if is_call else 0] += change_above

    print("Changed: puts:{} calls:{}".format(volume_call_put[0], volume_call_put[1]))
    print("Above Changed: puts:{} calls:{}".format(volume_call_put_above[0], volume_call_put_above[1]))

    # create plot
    volumes_aggr.sort(key=lambda x: x[1], reverse=True)
    volumes_aggr = [exercise_date for exercise_date, _ in volumes_aggr[:3]]
    for exercise_date, is_call, date_list, strike_set in data:
        if exercise_date not in volumes_aggr:
            continue
        n_groups = len(strike_set)
        #print(exercise_date, n_groups, len(strike_set))
        #fig, ax = plt.subplots()
        plt.subplot(211 if is_call else 212)
        plt.plot()
        index = np.arange(n_groups)
        bar_width = 0.2
        opacity = 0.8
        strikes = list(strike_set)
        strikes.sort()
        strike_dates = [[] for _ in range(len(strikes))]
        idx = 0

        for date, strike_list in date_list:
            at_close_list = [0] * len(strikes)
            i = 0
            for strike, at_close in strike_list:
                while strikes[i] != strike:
                    strike_dates[i].append(0)
                    i += 1
                at_close_list[i] = at_close
                strike_dates[i].append(at_close)
                i += 1
            while i<len(strike_dates):
                strike_dates[i].append(0)
                i += 1
            #print(len(at_close_list))
            plt.bar(index + idx*bar_width, at_close_list, bar_width,
                    alpha=opacity,
                    label=date.strftime("%m-%d"))
                    #color='b',
                    #label='Frank')
            idx += 1
        for i in range(len(strike_dates)):
            #print(strikes[i], strike_dates[i])
            strike_dates[i] = (strikes[i], strike_dates[i][-1] - strike_dates[i][-2])
        strike_dates.sort(key=lambda x : abs(x[1]), reverse=True)
        print(product, exercise_date.strftime("%m"), "Puts" if is_call==0 else "Calls", strike_dates[:5])

        plt.xlabel('Strikes')
        plt.ylabel('Interests')
        plt.title('Options of {} {} {}'.format(product, exercise_date.strftime("%m"), "Puts" if is_call==0 else "Calls"))
        plt.xticks(index + bar_width, strikes, rotation=90, fontsize=6)
        plt.legend()
        plt.tight_layout()
        #plt.switch_backend('TkAgg')
        #plt.switch_backend('wxAgg')
        #plt.switch_backend('QT4Agg')
        #mng = plt.get_current_fig_manager()
        #mng.window.state('zoomed')
        #mng.frame.Maximize(True)
        #mng.window.showMaximized()
        if not is_call:
            plt.show()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Option Analysis")
    parser.add_argument("--date", type=str, help="report date")
    parser.add_argument("--product", type=str, help="option product")
    parser.add_argument("--price", type=str, help="current price")
    args = parser.parse_args()

    main(args)
