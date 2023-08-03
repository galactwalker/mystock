import sqlite3
from datetime import datetime

import pandas as pd
import tushare as ts
import time

"""
用于全局数据的第一次采集，及新建数据库。日常更新另寻日常更新类。
    机构调研（surv_date）：   每天限访问5次，故不能按个股使用，只能按surv_date集中获取数据。
                            
"""


class TushareGlobalNew:

    def __init__(self):

        self.pro = ts.pro_api('19574700f2ce77bbbc2bb9214c24045c88841297b481ac546b67f5cc')

        self.thisday = int(str(datetime.now().year) + str(datetime.now().month).rjust(2, '0') \
                   + str(datetime.now().day).rjust(2, '0'))          # 取current date。 rjust(2,'0')用来补0
        self.thisday_20ybefore = str(self.thisday-200000)
        self.thisday_20ybefore_1 = str(self.thisday-200000-1)

        # 创建连接，每一个getData方法都可以用到。连接的close作为单独的方法，使用者可以灵活close连接。
        self.conn = sqlite3.connect('D:/financeDB/StockGlobal.sqlite')    # 借助%s把变量植入路径，用股票名创建sqlite文件
        self.cur = self.conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

    # 15股票列表（全局）        （虽大，但一次就可以获取）
    def getData_stock_basic_global(self):
        # tushare to dataframe
        df_stock_global = self.pro.stock_basic(**{"ts_code": "",
            "name": "", "exchange": "", "market": "", "is_hs": "", "list_status": "", "limit": "", "offset": ""
        }, fields=["ts_code", "symbol", "name", "area", "industry", "market", "list_date", "fullname", "enname",
                   "cnspell", "exchange", "curr_type", "list_status", "is_hs", "delist_date"])

        # dataframe to sqlite
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS StockGlobal "
            "(ts_code, symbol, name, area, industry, market, list_date, fullname, enname, cnspell, exchange, "
            "curr_type, list_status, is_hs, delist_date)")
        self.conn.commit()
        df_stock_global.to_sql('StockGlobal', con=self.conn, if_exists='append', index=False)

    # 16交易日历（全局）（更新频率一年）   （虽大，但一次就可以获取）
    def getData_trade_cal(self):
        # tushare to dataframe
        df_tradecal = self.pro.trade_cal(**{"exchange": "", "cal_date": "", "start_date": "", "end_date": "",
                    "is_open": "", "limit": "", "offset": ""
                    }, fields=["cal_date", "is_open"])
        df_tradecal = df_tradecal.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS tradecal (cal_date, is_open)")
        self.conn.commit()
        df_tradecal.to_sql('tradecal', con=self.conn, if_exists='append', index=False)   # if_exists针对表是否存在

    def close(self):        # 使操作者可以自主选择close的时间
        self.conn.close()

if __name__ == '__main__':
    tsd = TushareGlobalNew("000636.SZ")
    #tsd.getData_stk_surv()                  # 14机构调研（全局）
    tsd.getData_stock_basic_global()        # 15股票列表（全局）
    #tsd.getData_trade_cal()                 # 16交易日历（全局）

    tsd.close()
