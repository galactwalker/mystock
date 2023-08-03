import os
import sqlite3
import sys
import time

import pandas as pd
import tushare as ts

from datatosql.tusharestocknew import TushareStockNew
from datatosql.tusharestocknewspecial import TushareStockNewSpecial
from datatosql.tusharestockupdate import TushareStockUpdate


class TushareStockTotal:
    def __init__(self):
        self.stock_list = self.getStockList()
        self.pro = ts.pro_api('19574700f2ce77bbbc2bb9214c24045c88841297b481ac546b67f5cc')

    def getAllNew(self):
        tsNew = TushareStockNew()
        count = 0
        for stock_code in self.stock_list:
            filename = stock_code[7:9] + stock_code[0:6]
            if not os.path.exists(r"D:\financeDB\%s.sqlite" % filename):        # 如果文件不存在，下载
                tsNew.getDataAll(stock_code)
                print(stock_code+"下载完毕")
                count += 1
                if count == 50:
                    sys.exit()
                time.sleep(10)
            else:                                                               # 如果文件存在，跳过，继续下一个
                print(stock_code+"跳过")
                continue

    def getAllNew_bakdaily(self):              # 因为每天限50次，所以单列出来
        tsNews = TushareStockNewSpecial()
        count = 0
        for stock_code in self.stock_list:
            count_fromstock = tsNews.getData_bak_daily(stock_code)
            print(stock_code + "下载完毕")
            count += count_fromstock
            if count == 50:
                sys.exit()
            time.sleep(12*count_fromstock)

    def getAllNew_stksurv(self):              # 因为每天限50次，所以单列出来
        tsNews = TushareStockNewSpecial()
        count = 0
        for stock_code in self.stock_list:
            count_getdata = tsNews.getData_stk_surv(stock_code)
            print(stock_code + "下载完毕")
            count += count_getdata
            if count == 6:
                sys.exit()
            time.sleep(30*count_getdata)

    def getAllUpdate(self):
        tsUpdate = TushareStockUpdate()
        for stock_code in self.stock_list:
            tsUpdate.getDataAll(stock_code)
            print(stock_code + "下载完毕")
            time.sleep(10)

    def getStockList(self):                                         # 取的是“精选股票”的股票列表
        conn = sqlite3.connect(r"D:\financeDB\StockSelection.sqlite")

        sql_stockselection = "SELECT ts_code, name FROM StockGlobal"
        df_stockselection = pd.read_sql_query(sql_stockselection, conn)
        stockselection_list = df_stockselection['ts_code'].tolist()

        return stockselection_list

if __name__ == '__main__':
    tsTotal = TushareStockTotal()
    #tsTotal.getAllNew()
    #tsTotal.getAllNew_bakdaily()
    tsTotal.getAllNew_stksurv()
