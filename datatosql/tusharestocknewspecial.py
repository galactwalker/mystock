import sqlite3
from datetime import datetime

import pandas as pd
import tushare as ts
import time

from pandas import DataFrame

"""
与TushareStockNew()类相同，用于股票数据的第一次采集，及新建数据库。
本类用于特殊情况的处理。
    13.备用行情，因为接口限制50次/日，5次/分，所以单列到这里处理
    14.机构调研，因为接口限制5次/日，及200条/次，也单列到这里
    
        备用行情（类似资金流）trade_date：1.trade_date为空，新建new 2.trade_date为最新，不动 3.trade_date需要update
        机构调研（类似管理层） surv_date：1.surv_date为空，新建new 2.查询参数有start_date，不进行比较，直接start_date查询，update。

"""


class TushareStockNewSpecial:

    def __init__(self):
        self.pro = ts.pro_api('19574700f2ce77bbbc2bb9214c24045c88841297b481ac546b67f5cc')
        self.thisday = int(str(datetime.now().year) + str(datetime.now().month).rjust(2, '0') \
                   + str(datetime.now().day).rjust(2, '0'))         # 取current date。 rjust(2,'0')用来补0

    # 13备用行情    （主要用于获得总股本）（数据量本应与日线一样多，但tushare只追溯到17年，所以取1次就够）
    def getData_bak_daily(self, ts_code):

        # 创建连接。（从init方法转移到此，这样循环取个股数据时，可以避免每次取都要实例化TushareStockNew）
        filename = ts_code[7:9] + ts_code[:6]
        conn = sqlite3.connect('D:/financeDB/%s.sqlite' % filename)    # 借助%s把变量植入路径，用股票名创建sqlite文件
        cur = conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        # tushare to dataframe
        # 上来就创建表IF NOT EXISTS
        cur.execute(
            "CREATE TABLE IF NOT EXISTS bakdaily "
            "(ts_code, trade_date, name, turn_over, swing, selling, buying, total_share, float_share, industry, area, "
            "float_mv, total_mv, avg_price, avg_turnover, attack, interval_3, interval_6)")
        # 查询数据库中数据的最新日期，当然self.cur.fetchone()有可能是None，所以不能用来赋值
        cur.execute("SELECT trade_date FROM bakdaily ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        df_bak_daily = None
        count_getdata = 0                                       # 传递给total，取到数据赋值1，没有取到赋值0

        # 开始验证取值
        if cur.fetchone() is None:                             # 1数据库没有数据，需要new
            df_bak_daily = self.pro.bak_daily(**{"ts_code": ts_code,
                           "trade_date": "", "start_date": "", "end_date": "", "offset": "", "limit": ""
                           }, fields=["ts_code", "trade_date", "name", "turn_over", "swing", "selling", "buying",
                           "total_share", "float_share", "industry", "area", "float_mv", "total_mv", "avg_price",
                           "avg_turnover", "attack", "interval_3", "interval_6"])
            df_bak_daily = df_bak_daily.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
            count_getdata = 1
            # dataframe to sqlite
            df_bak_daily.to_sql('bakdaily', con=conn, if_exists='append', index=False)
        else:
            print(ts_code+"跳过备用行情")
            count_getdata = 0
            """
            cur.execute("SELECT trade_date FROM bakdaily ORDER BY ROWID DESC LIMIT 1")
            lastdate = int(cur.fetchone()[0])
            if lastdate == self.thisday:                        # 2数据库已经是最新
                print("总股本数据为最新")
                df_bak_daily = DataFrame()
            elif 0 < lastdate < self.thisday:                   # 3数据库有未更新数据，需要update
                df_bak_daily = self.pro.bak_daily(**{"ts_code": ts_code,
                             "trade_date": "", "start_date": lastdate+1, "end_date": "", "offset": "", "limit": ""
                             }, fields=["ts_code", "trade_date", "name", "turn_over", "swing", "selling", "buying",
                             "total_share", "float_share", "industry", "area", "float_mv", "total_mv", "avg_price",
                             "avg_turnover", "attack", "interval_3", "interval_6"])
                df_bak_daily = df_bak_daily.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
            """

        conn.close()

        return count_getdata

    # 14机构调研    （数据量较小）
    def getData_stk_surv(self, ts_code):
        # 创建连接。（从init方法转移到此，这样循环取个股数据时，可以避免每次取都要实例化TushareStockNew）
        filename = ts_code[7:9] + ts_code[:6]
        conn = sqlite3.connect('D:/financeDB/%s.sqlite' % filename)    # 借助%s把变量植入路径，用股票名创建sqlite文件
        cur = conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        # tushare to dataframe
        # 上来就创建表IF NOT EXISTS
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stksurv "
            "(ts_code, name, surv_date, fund_visitors, rece_place, rece_mode, rece_org, org_type, comp_rece, content)")
        # 查询数据库中数据的最新日期，当然self.cur.fetchone()有可能是None，所以不能直接用来赋值
        cur.execute("SELECT surv_date FROM stksurv ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        df_stk_surv = None
        count_getdata = 0       # 传递给total，取到数据赋值1，没有取到赋值0

        # 开始验证取值
        if cur.fetchone() is None:                             # 1数据库没有数据，需要new
            df_stk_surv = self.pro.stk_surv(**{"ts_code": ts_code,
                        "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""
                        }, fields=["ts_code", "name", "surv_date", "fund_visitors", "rece_place", "rece_mode",
                        "rece_org", "org_type", "comp_rece", "content"])
            df_stk_surv = df_stk_surv.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
            if df_stk_surv.empty:                                                   # 判断是否为空
                df_stk_surv = DataFrame(data=[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                            columns=["ts_code", "name", "surv_date", "fund_visitors", "rece_place", "rece_mode",
                            "rece_org", "org_type", "comp_rece", "content"])    # 若为空填入一行0，使它不为空，这样就表示new过了，以免下次浪费对接口的调用
            count_getdata = 1
            # dataframe to sqlite
            df_stk_surv.to_sql('stksurv', con=conn, if_exists='append', index=False)
        else:
            print(ts_code+"跳过机构调研")
            count_getdata = 0
            """
            cur.execute("SELECT surv_date FROM stksurv ORDER BY ROWID DESC LIMIT 1")
            lastdate = int(cur.fetchone()[0])
            df_stk_surv = self.pro.stk_surv(**{"ts_code": ts_code,
                        "trade_date": "", "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                        }, fields=["ts_code", "name", "surv_date", "fund_visitors", "rece_place", "rece_mode",
                        "rece_org", "org_type", "comp_rece", "content"])
            df_stk_surv = df_stk_surv.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
            """

        conn.close()

        return count_getdata


if __name__ == '__main__':
    tsds = TushareStockNewSpecial()

    tsds.getData_bak_daily("000636.SZ")                 # 13备用行情（主要用于获得总股本）
