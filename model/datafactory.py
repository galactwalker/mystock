import sqlite3
from datetime import datetime

import pandas as pd


class DataFactory:

    def __init__(self):
        self.stock_list = self.get_stock_list()

    def get_stock_list(self):
        select_conn = sqlite3.connect(r"D:\financeDB\StockRecycle.sqlite")
        sql_daily = "SELECT ts_code, symbol, name FROM stockre limit 0,150" # 取前150条
        self.data_stocks = pd.read_sql_query(sql_daily, select_conn, index_col='ts_code').sort_index(ascending=True)
        stock_list = self.data_stocks.index.tolist()
        return stock_list

    def analysed_stocks(self):
        predlist_stocks= []
        for stock in self.stock_list:
            predlist_1stock = self.analysed_1stock(stock)
            predlist_stockname = self.data_stocks.loc[stock, ['symbol', 'name']].tolist()
            print(predlist_stockname + predlist_1stock)
            predlist_stocks.append(predlist_stockname + predlist_1stock)
        columns_stockname = ['symbol', 'name']
        columns_moneyflow = ['ed30', 'ed60', 'ed100', 'ed200', 'et30', 'et60', 'et200', 'ld30', 'ld60', 'ld100', 'ld200',
                             'lt30', 'lt60', 'lt200', 'sd30', 'sd60', 'sd100', 'sd200', 'st30', 'st60', 'st200']
        columns_hkhold = ['hd30', 'hd60', 'hd100', 'hd200', 'ht30', 'ht60', 'ht200']
        columns_margindetails = ['md30', 'md60', 'mt30', 'mt60', 'mt200']
        columns_stk_holdertrade = ['sum1']

        columns_pred = columns_stockname + columns_moneyflow + columns_hkhold + columns_margindetails + columns_stk_holdertrade
        df_prediction = pd.DataFrame(predlist_stocks, index=self.stock_list, columns=columns_pred)
        print(df_prediction)

        conn = sqlite3.connect('D:/financeDB/StockPrediction.sqlite')
        df_prediction.to_sql('table1', con=conn, if_exists='replace', index=True)

    def analysed_1stock(self, ts_code):
        print(ts_code)
        filename = ts_code[7:9] + ts_code[0:6]
        stock_conn = sqlite3.connect(r"D:\financeDB\StockRecycle\%s.sqlite" % filename)

        # 取最近的总股本       总股本数据不全，暂以100亿代位
        # data_fromdb_bakdaily = self.dataFromDB_bakdaily(stock_conn)
        # self.total_share = data_fromdb_bakdaily.iloc[-1]['total_share']
        self.total_share = 10000000000

        # 取收盘价的df
        self.data_fromdb_daily = self.dataFromDB_daily(stock_conn)

        data_fromdb_moneyflow = self.dataFromDB_moneyflow(stock_conn)
        datalist_moneyflow = self.moneyflowData(data_fromdb_moneyflow)

        data_fromdb_hkhold = self.dataFromDB_hkhold(stock_conn)
        datalist_hkhold = self.hkholdData(data_fromdb_hkhold)
        
        data_fromdb_margindetail = self.dataFromDB_margindetail(stock_conn)
        datalist_margindetail = self.margindetailData(data_fromdb_margindetail)

        data_fromdb_stk_holdertrade = self.dataFromDB_stk_holdertrade(stock_conn)
        datalist_holdertrade_sum = self.stkholdertradeData(data_fromdb_stk_holdertrade)

        predlist_1stock = datalist_moneyflow + datalist_hkhold + datalist_margindetail + datalist_holdertrade_sum

        return predlist_1stock

    # 01日线
    def dataFromDB_daily(self, stock_conn):
        sql_daily = "SELECT trade_date, close FROM daily"  # limit -1 offset 1提取时不包含第一行，limit表示取多少行，-1意思无限制，offset表示偏离多少行，1表示偏离1行即从第2行开始(后来首行插入的中文列名删除了，也就不需要了)
        data_daily_fromdb = pd.read_sql_query(sql_daily, stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_daily_fromdb

    # 05资金流
    def dataFromDB_moneyflow(self, stock_conn):
        sql_moneyflow = "SELECT trade_date,buy_lg_vol,sell_lg_vol,buy_elg_vol,sell_elg_vol FROM moneyflow"
        data_fromdb_moneyflow = pd.read_sql_query(sql_moneyflow, stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_fromdb_moneyflow

    # 06港资
    def dataFromDB_hkhold(self, stock_conn):
        sql_hkhold = "SELECT trade_date, vol, ratio FROM hkhold"
        data_hkhold_fromdb = pd.read_sql_query(sql_hkhold, stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_hkhold_fromdb

    # 09融资融券
    def dataFromDB_margindetail(self, stock_conn):
        sql_margindetail = "SELECT trade_date, rzye FROM margindetail"
        data_margindetail_fromdb = pd.read_sql_query(sql_margindetail, stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_margindetail_fromdb

    # 10股东增减持
    def dataFromDB_stk_holdertrade(self, stock_conn):
        sql_stk_holdertrade = "SELECT ann_date, in_de, change_vol FROM stkholdertrade"
        data_stk_holdertrade_fromdb = pd.read_sql_query(sql_stk_holdertrade, stock_conn, index_col='ann_date').sort_index(ascending=True)
        return data_stk_holdertrade_fromdb

    # 13备用行情（主要用于获得总股本）
    def dataFromDB_bakdaily(self, stock_conn):
        sql_bak_daily = "SELECT trade_date, total_share FROM bakdaily"
        data_bakdaily_fromdb = pd.read_sql_query(sql_bak_daily, stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_bakdaily_fromdb

    def moneyflowData(self, data_fromdb_moneyflow):
        data_moneyflownetelg = []
        data_moneyflownetlg = []
        data_moneyflownetsum = []
        for trade_date, row in data_fromdb_moneyflow.iterrows():      # dataframe的iterrows()迭代器会返回每一行
            buy_lg, sell_lg, buy_elg, sell_elg = row[:4]
            # 超大单净值
            net_elg = buy_elg-sell_elg
            data_moneyflownetelg.append(net_elg)
            # 大单净值
            net_lg = buy_lg-sell_lg
            data_moneyflownetlg.append(net_lg)
            # 合计净值
            net_total = buy_elg-sell_elg+buy_lg-sell_lg
            data_moneyflownetsum.append(net_total)

        # 超大单
        mfelg30 = data_moneyflownetelg[-30:]
        mfelg60 = data_moneyflownetelg[-60:]
        print(mfelg60)
        mfelg100 = data_moneyflownetelg[-100:]
        mfelg200 = data_moneyflownetelg[-200:]

        elg_pdays30 = len([i for i in mfelg30 if i > 0]) if len([i for i in mfelg30 if i > 0])>20 else 0          # 超过20日显示，未超过显示0
        elg_pdays60 = len([i for i in mfelg60 if i > 0]) if len([i for i in mfelg60 if i > 0])>40 else 0
        elg_pdays100 = len([i for i in mfelg100 if i > 0]) if len([i for i in mfelg100 if i > 0])>60 else 0
        elg_pdays200 = len([i for i in mfelg200 if i > 0]) if len([i for i in mfelg200 if i > 0])>120 else 0
        elg_total30 = sum(mfelg30)/self.total_share if sum(mfelg30)/self.total_share>0.01 else 0
        elg_total60 = sum(mfelg60)/self.total_share if sum(mfelg60)/self.total_share>0.02 else 0
        elg_total200 = sum(mfelg200)/self.total_share if sum(mfelg200)/self.total_share>0.05 else 0

        # 大单
        mflg30 = data_moneyflownetlg[-30:]
        mflg60 = data_moneyflownetlg[-60:]
        mflg100 = data_moneyflownetlg[-100:]
        mflg200 = data_moneyflownetlg[-200:]

        lg_pdays30 = len([i for i in mflg30 if i > 0]) if len([i for i in mflg30 if i > 0])>20 else 0
        lg_pdays60 = len([i for i in mflg60 if i > 0]) if len([i for i in mflg60 if i > 0])>40 else 0
        lg_pdays100 = len([i for i in mflg100 if i > 0]) if len([i for i in mflg100 if i > 0])>60 else 0
        lg_pdays200 = len([i for i in mflg200 if i > 0]) if len([i for i in mflg200 if i > 0])>120 else 0
        lg_total30 = sum(mflg30)/self.total_share if sum(mflg30)/self.total_share>0.01 else 0
        lg_total60 = sum(mflg60)/self.total_share if sum(mflg60)/self.total_share>0.02 else 0
        lg_total200 = sum(mflg200)/self.total_share if sum(mflg200)/self.total_share>0.05 else 0

        # 合计
        mfsum30 = data_moneyflownetsum[-30:]
        mfsum60 = data_moneyflownetsum[-60:]
        mfsum100 = data_moneyflownetsum[-100:]
        mfsum200 = data_moneyflownetsum[-200:]

        sum_pdays30 = len([i for i in mfsum30 if i > 0]) if len([i for i in mfsum30 if i > 0])>20 else 0
        sum_pdays60 = len([i for i in mfsum60 if i > 0]) if len([i for i in mfsum60 if i > 0])>40 else 0
        sum_pdays100 = len([i for i in mfsum100 if i > 0]) if len([i for i in mfsum100 if i > 0])>60 else 0
        sum_pdays200 = len([i for i in mfsum200 if i > 0]) if len([i for i in mfsum200 if i > 0])>120 else 0
        sum_total30 = sum(mfsum30)/self.total_share if sum(mfsum30)/self.total_share>0.01 else 0
        sum_total60 = sum(mfsum60)/self.total_share if sum(mfsum60)/self.total_share>0.02 else 0
        sum_total200 = sum(mfsum200)/self.total_share if sum(mfsum200)/self.total_share>0.05 else 0

        list_mf = [elg_pdays30, elg_pdays60, elg_pdays100, elg_pdays200, elg_total30, elg_total60, elg_total200,
                lg_pdays30, lg_pdays60, lg_pdays100, lg_pdays200, lg_total30, lg_total60, lg_total200,
                sum_pdays30, sum_pdays60, sum_pdays100, sum_pdays200, sum_total30, sum_total60, sum_total200]
        return list_mf

    def hkholdData(self, data_fromdb_hkhold):
        data_hkhold = []
        last_vol = 0
        for trade_date, row in data_fromdb_hkhold.iterrows():  # dataframe的iterrows()迭代器会返回每一行
            vol, ratio = row[:2]
            change = vol - last_vol
            data_hkhold.append(change)
            last_vol = vol

        hksum30 = data_hkhold[-30:]
        hksum60 = data_hkhold[-60:]
        hksum100 = data_hkhold[-100:]
        hksum200 = data_hkhold[-200:]

        hk_pdays30 = len([i for i in hksum30 if i > 0]) if len([i for i in hksum30 if i > 0])>20 else 0
        hk_pdays60 = len([i for i in hksum60 if i > 0]) if len([i for i in hksum60 if i > 0])>40 else 0
        hk_pdays100 = len([i for i in hksum100 if i > 0]) if len([i for i in hksum100 if i > 0])>60 else 0
        hk_pdays200 = len([i for i in hksum200 if i > 0]) if len([i for i in hksum200 if i > 0])>120 else 0
        hk_total30 = sum(hksum30)/self.total_share if sum(hksum30)/self.total_share>0.01 else 0
        hk_total60 = sum(hksum60)/self.total_share if sum(hksum60)/self.total_share>0.02 else 0
        hk_total200 = sum(hksum200)/self.total_share if sum(hksum200)/self.total_share>0.05 else 0

        list_hk = [hk_pdays30, hk_pdays60, hk_pdays100, hk_pdays200, hk_total30, hk_total60, hk_total200]
        return list_hk

    def margindetailData(self, data_fromdb_margindetail):
        df_margin_daily = pd.merge(data_fromdb_margindetail, self.data_fromdb_daily, left_index=True, right_index=True, how="left")
        df_margin_daily['rzyl'] = df_margin_daily['rzye'] / df_margin_daily['close']

        data_margindetail = []
        last_rzyl = 0
        for trade_date, row in df_margin_daily.iterrows():  # dataframe的iterrows()迭代器会返回每一行
            rzye, close, rzyl = row[:3]
            change = rzyl - last_rzyl
            data_margindetail.append(change)
            last_rzyl = rzyl

        mgsum30 = data_margindetail[-30:]
        mgsum60 = data_margindetail[-60:]
        mgsum200 = data_margindetail[-200:]

        mg_pdays30 = len([i for i in mgsum30 if i > 0]) if len([i for i in mgsum30 if i > 0])>20 else 0
        mg_pdays60 = len([i for i in mgsum60 if i > 0]) if len([i for i in mgsum60 if i > 0])>40 else 0
        mg_total30 = sum(mgsum30)/self.total_share if sum(mgsum30)/self.total_share>0.01 else 0
        mg_total60 = sum(mgsum60)/self.total_share if sum(mgsum60)/self.total_share>0.02 else 0
        mg_total200 = sum(mgsum200)/self.total_share if sum(mgsum200)/self.total_share>0.05 else 0

        list_mg = [mg_pdays30, mg_pdays60, mg_total30, mg_total60, mg_total200]
        return list_mg

    # 股东增减持
    def stkholdertradeData(self, data_fromdb_stk_holdertrade):          # 就取一年内增加之和，看是否大于总股本的1%

        oneyearbefore = str(datetime.now().year-1) + str(datetime.now().month).rjust(2, '0') \
                        + str(datetime.now().day).rjust(2, '0')             # 取一年前的date。 rjust(2,'0')用来补0
        str_list = data_fromdb_stk_holdertrade.index.tolist()               # index是ann_date
        int_list = [int(x) for x in str_list]
        anndate_oneyear_list = [x for x in int_list if x > int(oneyearbefore)]   # 一年内的ann_date
        if len(anndate_oneyear_list) > 0:                                        # anndate_oneyear_list有可能为空
            anndate_oneyear = min([x for x in int_list if x > int(oneyearbefore)])  # 取距一年前最近的ann_date

            index_loc = data_fromdb_stk_holdertrade.index.get_loc(str(anndate_oneyear))     # 通过anndate_oneyear的index取得anndate_oneyear的行号(注意可能是一个列表）
            index_loc = index_loc if isinstance(index_loc, int) else index_loc.stop         # 如果是列表，取最大的
            print(index_loc)
            df_inoneyear = data_fromdb_stk_holdertrade.iloc[index_loc:]                     # 通过行号向大日期切片，得到一年以内的日期
            sum_in = df_inoneyear.loc[df_inoneyear['in_de'] == 'in', 'change_vol'].sum()    # 求大股东一年内买进总额
            sum_de = df_inoneyear.loc[df_inoneyear['in_de'] == 'de', 'change_vol'].sum()    # 求大股东一年内卖出总额
            sumyear_holdertrade = [(sum_in-sum_de)/self.total_share if (sum_in-sum_de)/self.total_share > 0.01 else 0]
        else:
            sumyear_holdertrade = [0]

        return sumyear_holdertrade



if __name__ == '__main__':
    df = DataFactory()
    df.analysed_stocks()
