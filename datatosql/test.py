import os
import sqlite3

import keyboard as keyboard
import pandas
import pandas as pd
#
# a = pandas.DataFrame([[1,2,3], [4,5,6], [7,8,9]], columns=['a','b','c'])
#
#
#
# ts_code = "002617.SZ"
# filename = ts_code[7:9] + ts_code[0:6]
# stock_conn = sqlite3.connect(r"D:\financeDB\%s.sqlite" % filename)
#
# sql_bak_daily = "SELECT trade_date, total_share FROM bakdaily"
# data_bakdaily_fromdb = pd.read_sql_query(sql_bak_daily, stock_conn, index_col='trade_date').sort_index(ascending=True)
# print(data_bakdaily_fromdb)

def abc(x):
    print(x)
    print("111")
h
keyboard.hook(abc)
#按下任何按键时，都会调用abc，其中一定会传一个值，就是键盘事件
keyboard.wait()

