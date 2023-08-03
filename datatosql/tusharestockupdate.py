import sqlite3
from datetime import datetime

import pandas as pd
import tushare as ts
import time
"""
用于股票数据日常更新，要的就是短又快。
"""


class TushareStockUpdate:

    def __init__(self):

        self.pro = ts.pro_api('19574700f2ce77bbbc2bb9214c24045c88841297b481ac546b67f5cc')

        self.thisday = int(str(datetime.now().year) + str(datetime.now().month).rjust(2, '0') \
                   + str(datetime.now().day).rjust(2, '0'))          # 取current date。 rjust(2,'0')用来补0
        self.thisday_20ybefore = str(self.thisday-200000)
        self.thisday_20ybefore_1 = str(self.thisday-200000-1)

    def getDataAll(self, ts_code):
        self.ts_code = ts_code

        # 创建连接，每一个getData方法都可以用到。连接的close作为单独的方法，使用者可以灵活close连接。（从init方法转移到此，这样循环取个股数据时，可以避免每次取都要实例化TushareStockNew）
        filename = self.ts_code[7:9] + self.ts_code[:6]
        self.conn = sqlite3.connect('D:/financeDB/%s.sqlite' % filename)    # 借助%s把变量植入路径，用股票名创建sqlite文件
        self.cur = self.conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        self.getData_daily()                    # 01日线
        time.sleep(2)
        self.getData_stockcompany()             # 02公司基本信息
        time.sleep(1)
        self.getData_managers()                 # 03管理层
        time.sleep(1)
        self.getData_stk_rewards()              # 04管理层薪酬及持股
        time.sleep(1)
        self.getData_moneyflow()                # 05资金流
        time.sleep(1)
        self.getData_hk_hold()                  # 06港资
        time.sleep(1)
        self.getData_top10holders()             # 07前十股东
        time.sleep(1)
        self.getData_top10floatholders()        # 08前十流通股东
        time.sleep(1)
        self.getData_margin_detail()            # 09融资融券
        time.sleep(1)
        self.getData_stk_holdertrade()          # 10股东增减持
        time.sleep(1)
        self.getData_stk_holdernumber()         # 11股东人数
        time.sleep(1)
        self.getData_adj_factor()               # 12复权因子
        time.sleep(2)
        self.getData_bak_daily()                # 13备用行情（主要用于获得总股本）

        self.conn.close()

    # 01日线数据    （单次限6000条，对于上市比较久的公司，需要分两次取完）
    def getData_daily(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT trade_date FROM daily ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_daily = None
        # 开始验证取值
        if lastdate == self.thisday:                            # 1数据库已经是最新
            print("日线数据为最新")
        elif 0 < lastdate < self.thisday:                       # 2数据库有未更新数据，需要update
            df_daily = self.pro.daily(**{"ts_code": self.ts_code,
                     "trade_date": "", "start_date": lastdate+1, "end_date": "", "offset": "", "limit": ""
                     }, fields=["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change",
                     "pct_chg", "vol", "amount"])
            df_daily = df_daily.iloc[::-1]              # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
        else:                                                   # 3其他情况一定有问题
            print("有问题")

        # dataframe to sqlite
        df_daily.to_sql('daily', con=self.conn, if_exists='append', index=False)        # if_exists='append'，指的是表是否存在，而不是数据是否存在

    # 02公司基本信息数据    (数据量1条)
    def getData_stockcompany(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT ann_date FROM stock_company ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        # 开始验证取值。情况比较特殊，没有start_date，只能先取出tushare数据然后跟数据库最新一条比对，相同，传空值，不同，以tushare数据update
        df_stockcom = self.pro.stock_company(**{"ts_code": self.ts_code,
                    "exchange": "", "status": "", "limit": "", "offset": ""
                    }, fields=["ts_code", "exchange", "chairman", "manager", "secretary", "reg_capital",
                    "setup_date", "province", "city", "website", "email", "employees", "introduction", "office",
                    "ann_date", "business_scope", "main_business"])
        if lastdate == int(df_stockcom['ann_date'][0]):
            df_stockcom = pd.DataFrame()        # 新建空dataframe，相当于赋空值
        else:
            pass

        # dataframe to sqlite
        df_stockcom.to_sql('stock_company', con=self.conn, if_exists='append', index=False)

    # 03管理层信息     (数据量小)
    def getData_managers(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT ann_date FROM managers ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_managers = None
        # 开始验证取值
        df_managers = self.pro.stk_managers(**{"ts_code": self.ts_code,
                    "ann_date": "", "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                    }, fields=["ts_code", "ann_date", "name", "gender", "lev", "title", "edu", "national",
                    "birthday", "begin_date", "end_date", "resume"])
        df_managers = df_managers.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_managers.to_sql('managers', con=self.conn, if_exists='append', index=False)

    # 04管理层薪酬和持股    (数据量小)
    def getData_stk_rewards(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT end_date FROM stkrewards ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastyear = int(self.cur.fetchone()[0][0:4])                  # 管理层薪酬及持股仅在年报公布，所以仅比较年份即可。
        thisyear = datetime.now().year
        df_stk_rewards = None
        # 开始验证取值
        if thisyear-lastyear > 1:
            yearlist = [(str(thisyear-i-1)+"1231") for i in range(thisyear-lastyear-1)]
            df_list = []
            for end_date in yearlist:
                df = self.pro.stk_rewards(**{"ts_code": self.ts_code,
                   "end_date": end_date, "limit": "", "offset": ""
                   }, fields=["ts_code", "ann_date", "end_date", "name", "title", "reward", "hold_vol"])
                df_list.append(df)
            df_stk_rewards = pd.concat(df_list)
        elif thisyear-lastyear == 1:
            print("已经是最近数据")
            df_stk_rewards = pd.DataFrame()         # 新建，相当于赋空值
        else:
            print("错了")

        # dataframe to sqlite
        df_stk_rewards.to_sql('stkrewards', con=self.conn, if_exists='append', index=False)

    # 05资金流     (单次5000，目前数据追溯到2010年，一次可以取完）
    def getData_moneyflow(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT trade_date FROM moneyflow ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_moneyflow = None
        # 开始验证取值
        if lastdate == self.thisday:                            # 2数据库已经是最新
            print("资金流数据为最新")
        elif 0 < lastdate < self.thisday:                       # 3数据库有未更新数据，需要update
            df_moneyflow = self.pro.moneyflow(**{"ts_code": self.ts_code,
                         "trade_date": "", "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                         }, fields=["ts_code", "trade_date", "buy_sm_vol", "buy_sm_amount", "sell_sm_vol", "sell_sm_amount",
                         "buy_md_vol", "buy_md_amount", "sell_md_vol", "sell_md_amount", "buy_lg_vol", "buy_lg_amount",
                         "sell_lg_vol", "sell_lg_amount", "buy_elg_vol", "buy_elg_amount", "sell_elg_vol",
                         "sell_elg_amount", "net_mf_vol", "net_mf_amount", "trade_count"])
            df_moneyflow = df_moneyflow.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_moneyflow.to_sql('moneyflow', con=self.conn, if_exists='append', index=False)

    # 06港资      （数据量较小）
    def getData_hk_hold(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT trade_date FROM hkhold ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_hkhold = None
        # 开始验证取值
        if lastdate == self.thisday:                        # 2数据库已经是最新
            print("港资数据为最新")
        elif 0 < lastdate < self.thisday:                   # 3数据库有未更新数据，需要update
            df_hkhold = self.pro.hk_hold(**{"code": "", "ts_code": self.ts_code,
                        "trade_date": "", "start_date": lastdate+1, "end_date": "", "exchange": "", "limit": "", "offset": ""
                        }, fields=["code", "trade_date", "ts_code", "name", "vol", "ratio", "exchange"])
            df_hkhold = df_hkhold.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_hkhold.to_sql('hkhold', con=self.conn, if_exists='append', index=False)

    # 07十大股东    （数据量较小）
    def getData_top10holders(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT end_date FROM top10holders ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_top10holders = None
        # 开始取值
        df_top10holders = self.pro.top10_holders(**{"ts_code": self.ts_code,
                        "period": "", "ann_date": "", "start_date": lastdate+1, "end_date": "", "offset": "", "limit": ""
                        }, fields=["ts_code", "ann_date", "end_date", "holder_name", "hold_amount", "hold_ratio"])
        df_top10holders = df_top10holders.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_top10holders.to_sql('top10holders', con=self.conn, if_exists='append', index=False)

    # 08十大流通股股东 （数据量较小）
    def getData_top10floatholders(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT end_date FROM top10floatholders ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_top10floatholders = None
        # 开始取值
        df_top10floatholders = self.pro.top10_floatholders(**{"ts_code": self.ts_code,
                             "period": "", "ann_date": "", "start_date": lastdate+1, "end_date": "", "offset": "", "limit": ""
                             }, fields=["ts_code", "ann_date", "end_date", "holder_name", "hold_amount"])
        df_top10floatholders = df_top10floatholders.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_top10floatholders.to_sql('top10floatholders', con=self.conn, if_exists='append', index=False)

    # 09融资融券    （数据量较小）
    def getData_margin_detail(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT trade_date FROM margindetail ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_margindetail = None
        # 开始验证取值
        if lastdate == self.thisday:                        # 2数据库已经是最新
            print("融资数据为最新")
        elif 0 < lastdate < self.thisday:                   # 3数据库有未更新数据，需要update
            df_margindetail = self.pro.margin_detail(**{"trade_date": "", "ts_code": self.ts_code,
                            "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                            }, fields=["trade_date", "ts_code", "rzye", "rqye", "rzmre", "rqyl", "rzche",
                            "rqchl", "rqmcl", "rzrqye", "name"])
            df_margindetail = df_margindetail.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_margindetail.to_sql('margindetail', con=self.conn, if_exists='append', index=False)

        """  tushare说明：
        本日融资余额(元) = 前日融资余额 + 本日融资买入 - 本日融资偿还额
        本日融券余量(股) = 前日融券余量 + 本日融券卖出量 - 本日融券买入量 - 本日现券偿还量
        本日融券余额(元) = 本日融券余量 × 本日收盘价
        """

    # 10股东增减持   （数据量极小）
    def getData_stk_holdertrade(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT ann_date FROM stkholdertrade ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_stkholdertrade = None
        # 开始验证取值
        df_stkholdertrade = self.pro.stk_holdertrade(**{"ts_code": self.ts_code,
                          "ann_date": "", "start_date": lastdate+1, "end_date": "", "trade_type": "", "holder_type": "",
                          "limit": "", "offset": ""
                          }, fields=["ts_code", "ann_date", "holder_name", "holder_type", "in_de", "change_vol", "change_ratio",
                          "after_share", "after_ratio", "avg_price", "total_share", "begin_date", "close_date"])
        df_stkholdertrade = df_stkholdertrade.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_stkholdertrade.to_sql('stkholdertrade', con=self.conn, if_exists='append', index=False)

    # 11股东人数    （数据量较小）
    def getData_stk_holdernumber(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期
        self.cur.execute("SELECT ann_date FROM stkholdernumber ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_stkholdernumber = None
        # 开始验证取值
        df_stkholdernumber = self.pro.stk_holdernumber(**{"ts_code": self.ts_code,
                           "enddate": "", "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                           }, fields=["ts_code", "ann_date", "end_date", "holder_num", "holder_nums"])
        df_stkholdernumber = df_stkholdernumber.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_stkholdernumber.to_sql('stkholdernumber', con=self.conn, if_exists='append', index=False)

    # 12复权因子    （单次限6000条，对于上市比较久的公司，需要分两次取完）
    def getData_adj_factor(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期，当然self.cur.fetchone()有可能是None，所以不能用来赋值
        self.cur.execute("SELECT trade_date FROM adjfactor ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_adj_factor = None
        # 开始验证取值
        if lastdate == self.thisday:                            # 2数据库已经是最新
            print("复权因子数据为最新")
        elif 0 < lastdate < self.thisday:                       # 3数据库有未更新数据，需要update
            df_adj_factor = self.pro.adj_factor(**{"ts_code": "000636.SZ",
                            "trade_date": "", "start_date": lastdate+1, "end_date": "", "limit": "", "offset": ""
                            }, fields=["ts_code", "trade_date", "adj_factor"])
            df_adj_factor = df_adj_factor.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转
        else:
            print("有问题")

        # dataframe to sqlite
        df_adj_factor.to_sql('adjfactor', con=self.conn, if_exists='append', index=False)

    # 13备用行情    （主要用于获得总股本，数据量本应与日线一样多，但tushare只追溯到17年，所以取1次就够）
    def getData_bak_daily(self):
        # tushare to dataframe
        # 查询数据库中数据的最新日期，当然self.cur.fetchone()有可能是None，所以不能用来赋值
        self.cur.execute("SELECT trade_date FROM bakdaily ORDER BY ROWID DESC LIMIT 1")    # SQLite提供ROWID这一虚拟列，它对每一行记录都有一个唯一的标识符。我们通过使用ORDER BY子句将查询结果按照ROWID字段进行逆序排列，并使用LIMIT子句限制结果只返回一条记录。这样就能够获取到最后一条记录了。
        lastdate = int(self.cur.fetchone()[0])
        df_bak_daily = None
        # 开始验证取值
        if lastdate == self.thisday:                        # 2数据库已经是最新
            print("融资数据为最新")
        elif 0 < lastdate < self.thisday:                   # 3数据库有未更新数据，需要update
            df_bak_daily = self.pro.bak_daily(**{"ts_code": self.ts_code,
                         "trade_date": "", "start_date": lastdate+1, "end_date": "", "offset": "", "limit": ""
                         }, fields=["ts_code", "trade_date", "name", "turn_over", "swing", "selling", "buying",
                         "total_share", "float_share", "industry", "area", "float_mv", "total_mv", "avg_price",
                         "avg_turnover", "attack", "interval_3", "interval_6"])
            df_bak_daily = df_bak_daily.iloc[::-1]  # tushare时间是由大到小排序的，不利于更新后数据的有序性，所以整体反转

        # dataframe to sqlite
        df_bak_daily.to_sql('bakdaily', con=self.conn, if_exists='append', index=False)

    def close(self):        # 使操作者可以自主选择close的时间
        self.conn.close()

if __name__ == '__main__':
    tsd = TushareStockUpdate("000636.SZ")
    #tsd.getDataAll()
    #tsd.getData_daily()                     # 01日线
    #tsd.getData_stockcompany()              # 02基本信息
    #tsd.getData_managers()                  # 03管理层
    #tsd.getData_stk_rewards()               # 04管理层薪酬及持股
    #tsd.getData_moneyflow()                 # 05资金流
    #tsd.getData_hk_hold()                   # 06港资
    #tsd.getData_top10holders()              # 07前十股东
    #tsd.getData_top10floatholders()         # 08前十流通股东
    #tsd.getData_margin_detail()             # 09融资融券
    #tsd.getData_stk_holdertrade()           # 10股东增减持
    #tsd.getData_stk_holdernumber()          # 11股东人数
    #tsd.getData_adj_factor()                # 12复权因子
    tsd.getData_bak_daily()                 # 13备用行情（主要用于获得总股本）

    tsd.close()
