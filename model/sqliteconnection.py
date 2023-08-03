import sqlite3
import pandas as pd
from pandas import DataFrame
"""
说明一下SQLite的资源占用问题：
SQLite通过把已经打开的数据库实例保存在内存中，这样在下一次访问时可以直接使用，不用频繁关闭数据库。
那么我们在mainwindow中，等单只股票的数据全部访问采集完之后，再关闭数据库。
"""


class SqliteConnection:
    def __init__(self, ts_code):
        self.ts_code = ts_code
        self.filename = self.ts_code[7:9] + self.ts_code[0:6]

        # 数据库连接
        self.stock_conn = sqlite3.connect(r"D:\financeDB\%s.sqlite" % self.filename)
        self.cur = self.stock_conn.cursor()
        self.global_conn = sqlite3.connect(r"D:\financeDB\StockGlobal.sqlite")

    # 01日线
    def dataFromDB_daily(self):
        sql_daily = "SELECT trade_date,open,high,low,close,vol FROM daily"  # limit -1 offset 1提取时不包含第一行，limit表示取多少行，-1意思无限制，offset表示偏离多少行，1表示偏离1行即从第2行开始(后来首行插入的中文列名删除了，也就不需要了)
        # pandas的read_sql_query()方法，直接读取sqlite数据库中的数据，并转换为dataframe格式的数据，参数：sql是sql语句，sz000636_conn是数据库连接，index_col设置索引列（默认自动添加索引列）
        data_daily_fromdb = pd.read_sql_query(sql_daily, self.stock_conn, index_col='trade_date').sort_index(ascending=True)  # sort_index(ascending=True)，dataframe数据顺向排序（因为顺序已经排好了，此处没有也可以）
        return data_daily_fromdb

    # 02公司基本信息
    def dataFromDB_stockcom(self):
        sql_stockcom = "SELECT exchange, chairman, manager, secretary, reg_capital, setup_date, province, city, " \
                       "website, employees, introduction, office, ann_date, business_scope, main_business " \
                       "FROM stock_company"
        data_stockcom_fromdb = pd.read_sql_query(sql_stockcom, self.stock_conn, index_col='ann_date').sort_index(ascending=True)
        return data_stockcom_fromdb

    # 03管理层
    def dataFromDB_managers(self):
        sql_managers = "SELECT ts_code, ann_date, name, gender, lev, title, edu, national, birthday, begin_date, " \
                       "end_date, resume FROM managers"
        data_managers_fromdb = pd.read_sql_query(sql_managers, self.stock_conn, index_col='ann_date').sort_index(ascending=True)
        return data_managers_fromdb

    # 04管理层薪酬及持股
    def dataFromDB_stkrewards(self):
        sql_stkrewards = "SELECT ts_code, ann_date, end_date, name, title, reward, hold_vol FROM stkrewards"
        data_stkrewards_fromdb = pd.read_sql_query(sql_stkrewards, self.stock_conn, index_col='end_date').sort_index(ascending=True)
        return data_stkrewards_fromdb

    # 05资金流
    def dataFromDB_moneyflow(self):
        sql_moneyflow = "SELECT trade_date,buy_lg_vol,sell_lg_vol,buy_elg_vol,sell_elg_vol FROM moneyflow"
        data_moneyflow_fromdb = pd.read_sql_query(sql_moneyflow, self.stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_moneyflow_fromdb

    # 06港资
    def dataFromDB_hkhold(self):
        sql_hkhold = "SELECT trade_date, vol, ratio FROM hkhold"
        data_hkhold_fromdb = pd.read_sql_query(sql_hkhold, self.stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_hkhold_fromdb

    # 07十大股东
    def dataFromDB_top10holders(self):
        sql_top10holders = "SELECT ts_code, ann_date, end_date, holder_name, hold_amount, hold_ratio FROM top10holders"
        data_top10holders_fromdb = pd.read_sql_query(sql_top10holders, self.stock_conn).sort_index(ascending=True)     # 不设index_col='end_date'，因为后面数据处理做透视表要用end_date
        return data_top10holders_fromdb

    # 08十大流通股股东
    def dataFromDB_top10floatholders(self):
        sql_top10floatholders = "SELECT ts_code, ann_date, end_date, holder_name, hold_amount FROM top10floatholders"
        data_top10floatholders_fromdb = pd.read_sql_query(sql_top10floatholders, self.stock_conn).sort_index(ascending=True)   # 不设index_col='end_date'，因为后面数据处理做透视表要用end_date
        return data_top10floatholders_fromdb

    # 09融资融券
    def dataFromDB_margindetail(self):
        sql_margindetail = "SELECT trade_date, ts_code, rzye, rqye, rzmre, rqyl, rzche, rqchl, rqmcl, rzrqye, name FROM margindetail"
        data_margindetail_fromdb = pd.read_sql_query(sql_margindetail, self.stock_conn, index_col='trade_date').sort_index(ascending=True)
        return data_margindetail_fromdb

    # 10股东增减持
    def dataFromDB_stk_holdertrade(self):
        sql_stk_holdertrade = "SELECT ts_code, ann_date, holder_name, holder_type, in_de, change_vol, change_ratio, " \
                              "after_share, after_ratio, avg_price, total_share, begin_date, close_date FROM stkholdertrade"
        data_stk_holdertrade_fromdb = pd.read_sql_query(sql_stk_holdertrade, self.stock_conn, index_col='ann_date').sort_index(ascending=True)
        return data_stk_holdertrade_fromdb

    # 13备用行情（主要用于获得总股本） 数据暂时不全临时措施
    def dataFromDB_bakdaily(self):
        sql_check = "SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name = 'bakdaily'"
        self.cur.execute(sql_check)
        if self.cur.fetchone()[0] > 0:
            sql_bak_daily = "SELECT trade_date, total_share FROM bakdaily"
            data_bakdaily_fromdb = pd.read_sql_query(sql_bak_daily, self.stock_conn, index_col='trade_date').sort_index(ascending=True)
        else:
            data_bakdaily_fromdb = DataFrame(columns=['trade_date', 'total_share'])      # 赋空值
        return data_bakdaily_fromdb

    # 16交易日历（全局）挪到了全局数据库中
    def dataFromDB_tradecal(self):
        sql_tradecal = "SELECT cal_date, is_open FROM tradecal limit -1 offset 1"       #！！！别忘记删除！！！
        data_tradecal_fromdb = pd.read_sql_query(sql_tradecal, self.global_conn, index_col='cal_date').sort_index(ascending=True)
        return data_tradecal_fromdb

    def close(self):
        self.stock_conn.close()
        self.global_conn.close()
