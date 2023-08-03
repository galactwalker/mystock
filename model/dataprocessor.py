from datetime import datetime

import pandas as pd


class DataProcessor:
    def __init__(self, data_fromdb_daily, data_fromdb_stockcom, data_fromdb_managers, data_fromdb_stkrewards,
                 data_fromdb_moneyflow, data_fromdb_hkhold, data_fromdb_top10holders, data_fromdb_top10floatholders,
                 data_fromdb_margindetail, data_fromdb_bakdaily, data_fromdb_tradecal):

        # 输入数据库数据（DataFrame）
        self.data_fromdb_daily = data_fromdb_daily
        self.data_fromdb_stockcom = data_fromdb_stockcom
        self.data_fromdb_managers = data_fromdb_managers        # 待做
        self.data_fromdb_stkrewards = data_fromdb_stkrewards    # 待做
        self.data_fromdb_moneyflow = data_fromdb_moneyflow
        self.data_fromdb_hkhold = data_fromdb_hkhold
        self.data_fromdb_top10holders = data_fromdb_top10holders
        self.data_fromdb_top10floatholders = data_fromdb_top10floatholders
        self.data_fromdb_margindetail = data_fromdb_margindetail
        self.data_fromdb_bakdaily = data_fromdb_bakdaily
        self.data_fromdb_tradecal = data_fromdb_tradecal

        # 输出数据（List）之 K线窗口（K线数据都是未复权的原始数据，需要补充一个前复权选项）
        self.data_kline_tradedate = self.data_fromdb_daily.index.tolist()
        self.data_kline_xmax = len(self.data_fromdb_daily)
        self.data_kline_ymax = self.data_fromdb_daily['high'].max()
        self.data_kline_open = self.data_fromdb_daily['open'].tolist()
        self.data_kline_close = self.data_fromdb_daily['close'].tolist()
        self.data_kline_high = self.data_fromdb_daily['high'].tolist()
        self.data_kline_low = self.data_fromdb_daily['low'].tolist()
        self.data_volume_ymax = self.data_fromdb_daily['vol'].max()

        self.data_kline_candlestick, self.data_volume, self.data_to_region = self.dailyData()       # 分别用于K线Item，成交量Item和region的初始化
        self.data_kline_list = [self.data_kline_xmax, self.data_kline_ymax, self.data_kline_tradedate,
                                self.data_kline_open, self.data_kline_close, self.data_kline_high, self.data_kline_low]     # 用于K线Plot
        self.data_volume_list = [self.data_kline_xmax, self.data_volume_ymax]                                               # 用于成交量Plot
        self.data_klineaxis_list = [self.data_kline_tradedate, self.data_kline_xmax]                                        # 用于Kline_axis

        # 输出数据（List）之 基本信息窗口
        self.data_stockcom = self.stockcomData()

        # 输出数据（List）之 资金流窗口
        self.data_moneyflowelg_xmax = len(self.data_fromdb_moneyflow)
        self.data_moneyflowelg_ymax = data_fromdb_moneyflow['buy_elg_vol'].max()
        self.data_moneyflowelg_ymin = -data_fromdb_moneyflow['sell_elg_vol'].max()
        self.data_moneyflownetelg_ymax = (data_fromdb_moneyflow['buy_elg_vol'] - data_fromdb_moneyflow['sell_elg_vol']).max()
        self.data_moneyflownetelg_ymin = (data_fromdb_moneyflow['buy_elg_vol'] - data_fromdb_moneyflow['sell_elg_vol']).min()
        self.data_moneyflowlg_ymax = data_fromdb_moneyflow['buy_lg_vol'].max()
        self.data_moneyflowlg_ymin = -data_fromdb_moneyflow['sell_lg_vol'].max()
        self.data_moneyflownetlg_ymax = (data_fromdb_moneyflow['buy_lg_vol'] - data_fromdb_moneyflow['sell_lg_vol']).max()
        self.data_moneyflownetlg_ymin = (data_fromdb_moneyflow['buy_lg_vol'] - data_fromdb_moneyflow['sell_lg_vol']).min()
        self.data_moneyflow_tradedate = self.data_fromdb_moneyflow.index.tolist()

        self.data_moneyflowelg, self.data_moneyflownetelg, self.data_moneyflowlg, self.data_moneyflownetlg = self.moneyflowData()                        # 分别用于moneyflowelg Item和moneyflowlg Item
        self.data_moneyflowelg_list = [self.data_moneyflowelg_xmax, self.data_moneyflowelg_ymax, self.data_moneyflowelg_ymin]   # 用于moneyflowelg Plot
        self.data_moneyflownetelg_list = [self.data_moneyflowelg_xmax, self.data_moneyflownetelg_ymax, self.data_moneyflownetelg_ymin]  # 用于moneyflownetelg Plot
        self.data_moneyflowlg_list = [self.data_moneyflowelg_xmax, self.data_moneyflowlg_ymax, self.data_moneyflowlg_ymin]      # 用于moneyflowlg Plot，x轴与moneyflowelg Plot相同
        self.data_moneyflownetlg_list = [self.data_moneyflowelg_xmax, self.data_moneyflownetlg_ymax, self.data_moneyflownetlg_ymin]     # 用于moneyflownetlg Plot
        self.data_moneyflowaxis_list = [self.data_moneyflow_tradedate, self.data_moneyflowelg_xmax]                 # 用于axis

        # 输出数据（List）之 港资窗口
        self.data_hkhold_xmax = len(self.data_fromdb_hkhold)
        self.data_hkhold_y_max = self.data_fromdb_hkhold['vol'].max()
        self.data_hkhold_tradedate = self.data_fromdb_hkhold.index.tolist()

        self.data_hkhold = self.hkholdData()                                                        # 用于hkhold Item
        self.data_hkhold_list = [self.data_hkhold_xmax, self.data_hkhold_y_max]                     # 用于hkhold Plot
        self.data_hkholdaxis_list = [self.data_hkhold_tradedate, self.data_hkhold_xmax]             # 用于hkholdaxis

        # 输出数据（List）之 资金总图
            # 生成标准交易日历
        indexNames = self.data_fromdb_tradecal[(self.data_fromdb_tradecal['is_open'] <= 0)].index   # ‘is_open’列，0休市1交易
        df_tradecal = self.data_fromdb_tradecal.drop(indexNames)                                    # 删除休市日，得到交易日
        df_tradecal.index.name = 'trade_date'                                   # 索引的名称由cal_date更改为trade_date
            # 标准交易日历中，超过今日的交易日需要删除
        last_tradedate = self.getLastTradedate(df_tradecal)                     # 成员方法getLastTradedate，寻找最近交易日的index（今日可能非交易日）
        index_loc = df_tradecal.index.get_loc(last_tradedate)                   # 通过last_tradedate的index取得last_tradedate的行号
        df_tradecal_current = df_tradecal.iloc[:index_loc+1]                    # 通过行号向小日期切片，去掉了超过今日的交易日
            # 港资数据（港资中有余额为0的情况，大概由于港股当日休市。对这种情况，在与融资合并后fillna(method='ffill')向后填充）
        df_hkhold_vol = self.data_fromdb_hkhold.drop(columns=['ratio'])
        df_hkhold_vol.rename(columns={'vol': 'hk_vol'}, inplace=True)           # inplace=True改写，不产生返回值。inplace=False另存，产生返回值。
            # 合并港资
        df_tradecal_hkhold = pd.merge(df_tradecal_current, df_hkhold_vol, left_index=True, right_index=True, how="left")   # merge连接，left左表，right右表。合并基准列，有索引用index，索引外其他列用on，how="outer"左合并="left"
            # 融资融券，取融资余量（融券占比仅1%舍弃），但是融资余量没有直接数据，用“融资余额/收盘价”近似估算
            # 1先合并融券表和日线表，2然后计算融资余量，3最后删除其他列，只保留trade_date和rzyl两列，得到df_margindetail_vol
        df_margin_daily = pd.merge(self.data_fromdb_margindetail, self.data_fromdb_daily, left_index=True, right_index=True, how="left")
        df_margin_daily['rzyl'] = df_margin_daily['rzye'] / df_margin_daily['close']                # dataframe中，列之间的计算，’rzyl‘若无可以自动创建
        df_margindetail_vol = df_margin_daily.drop(columns=['ts_code', 'rzye', 'rqye', 'rzmre', 'rqyl', 'rzche', 'rqchl',
                                                            'rqmcl', 'rzrqye', 'name', 'open', 'high', 'low', 'close', 'vol'])       # 融资余量已与东方财富数值比较验证，通过。
        df_margindetail_vol.rename(columns={'rzyl': 'mg_vol'}, inplace=True)
            # 合并融资
        df_tradecal_hkhold_margin = pd.merge(df_tradecal_hkhold, df_margindetail_vol, left_index=True, right_index=True, how="left")
        df_tradecal_hkhold_margin.fillna(method='ffill', inplace=True)  # 向下填充，港资休市的空缺。ffill向前，bfill向后，axis默认为按列向下。
        df_tradecal_hkhold_margin.fillna(0, inplace=True)  # 填补NAN为0，凡是在原dataframe更改，不向新变量赋值的，都需要inplace=True
            # 十大股东
        df_top10holders = pd.pivot_table(self.data_fromdb_top10holders, values='hold_amount', index='end_date', columns='holder_name', aggfunc='sum')
        date_list = ['0331', '0630', '0930', '1231']                                    # 季度末的日期
        indexNames = [i for i in df_top10holders.index if i[4:8] not in date_list]      # 数据清洗，找到end_date中的非季度末的日期
        df_top10holders_clean = df_top10holders.drop(index=indexNames)                  # 删除非季度末的日期数据（应当注意，这里有些零散数据被删除了）
        indexList_top10 = df_top10holders_clean.index.tolist()                          # index列end_date，转列表，以备下面排序
        df_top10holders_clean.sort_values(by=[i for i in indexList_top10], axis=1, ascending=False, inplace=True)     # 逐行排序，形成阶梯图
        df_top10holders_tail20 = df_top10holders_clean.tail(20)                         # 取最近5年的数据
        df_top10holders_washed = df_top10holders_tail20.dropna(axis=1, how='all', inplace=False)    # 删除全空值的列。how：任何值是空的’any’，所有值都是空的’all’。
        df_top10holders_sum = pd.DataFrame(df_top10holders_washed.sum(axis=1, skipna=True), columns=['holders_sum'])   # 求和。sum()得到Series对象，并且列noname。pd.DataFrame()方法用于将Series对象转换为DataFrame，同时columns参数为sum列命名
        df_top10holders_sum.index.name = 'trade_date'                            # 索引的名称由end_date更改为trade_date
            # 总股本
        self.data_fromdb_bakdaily.loc['20171017':, 'total_share'] = self.data_fromdb_bakdaily.loc['20171016':, 'total_share'] * 10000   # tushare的总股本数据中，自20171017开始，单位变为亿股，改回万股。
        data_total_share = self.data_fromdb_bakdaily['total_share'] * 10000
        data_total_share_standard = pd.merge(df_tradecal_current, data_total_share, left_index=True, right_index=True, how="left")    # 跟标准交易日历对齐
        data_total_share_standard.fillna(method='ffill', inplace=True)  # 向下填充，总股本数据偶尔有空缺。ffill向前，bfill向后，axis默认为按列向下。
        data_total_share_standard.fillna(0, inplace=True)  # 填补NAN为0。凡是在原dataframe更改，不向新变量赋值的，都需要inplace=True
            # 生成曲线数据，传递给capital
        df_tradecal_hkhold_margin['m_hk_sum'] = df_tradecal_hkhold_margin['mg_vol'] + df_tradecal_hkhold_margin['hk_vol']
        curvedata1 = df_tradecal_hkhold_margin['mg_vol'].tolist()                   # 第一条折线面积是融券，折线的值是融券
        curvedata2 = df_tradecal_hkhold_margin['m_hk_sum'].tolist()                 # 第二条折线面积是港资，折线的值是融券+港资
        curvedata3 = data_total_share_standard['total_share'].tolist()              # 总的面积是总股本，第三条折线的值是总股本
        self.data_caspital = [curvedata1, curvedata2, curvedata3]                   # 把三个折线的数据传向资金总图
            # 标准交易日历的数据传输给capitalaxis
        self.data_capitalaxis_tradedate = df_tradecal_current.index.tolist()
        self.data_capitalaxis_xmax = len(df_tradecal_current)
        self.data_capitalaxis_list = [self.data_capitalaxis_tradedate, self.data_capitalaxis_xmax]


            # 十大流通股东
        df_top10floatholders = pd.pivot_table(self.data_fromdb_top10floatholders, values='hold_amount', index='end_date', columns='holder_name', aggfunc='sum')
        indexList_top10f = df_top10floatholders.index.tolist()
        df_top10floatholders.sort_values(by=[i for i in indexList_top10f], axis=1, ascending=False, inplace=True)  # 逐行排序，形成阶梯图
        df_top10floatholders_tail20 = df_top10floatholders.tail(20)           # 取最近5年的数据
        df_top10floatholders_washed = df_top10floatholders_tail20.dropna(axis=1, how='all', inplace=False)  # 删除全空值的列。how：任何值是空的’any’，所有值都是空的’all’。

            # 管理层持股
        df_stkrewards = pd.pivot_table(self.data_fromdb_stkrewards, values='hold_vol', index='end_date', columns='name', aggfunc='sum')
        df_stkrewards.index.name = 'trade_date'  # 索引的名称由end_date更改为trade_date

        """
                df_stkrewards_vol.to_excel('D:/test.xlsx')
        writer = pd.ExcelWriter('D:/test.xlsx')                         # 如果要追加写入必须用ExcelWriter
        df_top10holders_washed.to_excel(writer, sheet_name='sheet1')
        df_top10floatholders_forcapital.to_excel(writer, sheet_name='sheet2')
        writer.close()                                                  # 加writer.close()才能写入文件成功，why？
        
            # 合并十大
        df_tradecal_hkhold_margin_top10sum = pd.merge(df_tradecal_hkhold_margin, df_top10holders_sum,
                                                   left_index=True, right_index=True, how="outer")
        
        """
        """
        删除全0行  df.loc[(df!=0).any(axis=1)]
        这段代码中，(df!=0)结果为一个布尔值的数据框，其中值为True表示该位置上的元素不为0。使用any函数可以包含数据框的每行或每列，
        因此any(axis=1)对于每行应返回一个值。我们使用这个结果来定位行中至少有一个非零值的行。.loc方法用于选择这些行。
        删除全0列  df = df.loc[:,~(df == 0).any(axis=0)]    未测试
        """

    def dailyData(self):
        data_list_kline = []                                # 准备传给klineitem的
        data_list_volume = []                               # 准备传给成交量Item的
        data_to_region = []                                 # 准备传给region_plot的一维数组
        index = 0
        for trade_date, row in self.data_fromdb_daily.iterrows():       # dataframe的iterrows()迭代器会返回每一行
            open, high, low, close, vol = row[:5]                       # 取出开盘价，最高价，最低价，收盘价，成交量
            datas_kline = (index, open, close, low, high)               # 添加一个序列index作为首列，并对开盘价，最高价，最低价，收盘价重新排序
            data_list_kline.append(datas_kline)
            datas_volume = (index, open, close, vol)                    # 添加一个序列index作为首列，并取出开盘价，收盘价，成交量
            data_list_volume.append(datas_volume)
            data_to_region.append(close)
            index += 1
        return data_list_kline, data_list_volume, data_to_region

    def stockcomData(self):
        datas = []
        for ann_date, row in self.data_fromdb_stockcom.iterrows():      # dataframe的iterrows()迭代器会返回每一行
            exchange, chairman, manager, secretary, reg_capital, setup_date, province, city, website, employees, introduction, office, business_scope, main_business = row[:14]    # 取出数据
            datas = [ann_date, exchange, chairman, manager, secretary, reg_capital, setup_date, province, city, employees, office, website, introduction, business_scope, main_business]     # 重新排序
        return datas

    def moneyflowData(self):
        data_moneyflowelg = []
        data_moneyflownetelg = []
        data_moneyflowlg = []
        data_moneyflownetlg = []
        index = 0
        for trade_date, row in self.data_fromdb_moneyflow.iterrows():      # dataframe的iterrows()迭代器会返回每一行
            buy_lg, sell_lg, buy_elg, sell_elg = row[:4]
            # 超大单
            datas_elg = (index, buy_elg, sell_elg)               # 添加一个序列index作为首列
            data_moneyflowelg.append(datas_elg)
            # 超大单净值
            datas_netP_elg = buy_elg-sell_elg if buy_elg-sell_elg>0 else 0
            datas_netN_elg = 0 if buy_elg-sell_elg > 0 else -(buy_elg-sell_elg)
            datas_net_elg = (index, datas_netP_elg, datas_netN_elg)
            data_moneyflownetelg.append(datas_net_elg)
            # 大单
            datas_lg = (index, buy_lg, sell_lg)               # 添加一个序列index作为首列
            data_moneyflowlg.append(datas_lg)
            # 大单净值
            datas_netP_lg = buy_lg-sell_lg if buy_lg-sell_lg > 0 else 0
            datas_netN_lg = 0 if buy_lg-sell_lg > 0 else -(buy_lg-sell_lg)
            datas_net_lg = (index, datas_netP_lg, datas_netN_lg)
            data_moneyflownetlg.append(datas_net_lg)

            index += 1
        return data_moneyflowelg, data_moneyflownetelg, data_moneyflowlg, data_moneyflownetlg

    def hkholdData(self):
        data_hkhold_list = []
        index = 0
        for trade_date, row in self.data_fromdb_hkhold.iterrows():      # dataframe的iterrows()迭代器会返回每一行
            vol, ratio = row[:2]
            datas = (index, vol, ratio)               # 添加一个序列index作为首列
            data_hkhold_list.append(datas)
            index += 1
        return data_hkhold_list

    # 当今日非交易日时，寻找最近的交易日
    def getLastTradedate(self, df_tradecal):
        df_lastyear = df_tradecal.tail(250).index                   # 取出标准交易日dataframe中的最近250个交易日
        str_list = df_lastyear.tolist()                             # dataframe转list
        int_list = [int(x) for x in str_list]                       # list中的全部string转int，便于比较

        currdate = str(datetime.now().year) + str(datetime.now().month).rjust(2, '0') \
                   + str(datetime.now().day).rjust(2, '0')          # 取current date。 rjust(2,'0')用来补0
        int_currdate = int(currdate)                                # current date转int，便于比较
        last_tradedate = max([x for x in int_list if x < int_currdate])     # 先取出int_list中比int_currdate小的全部值，然后找最大的那个
        last_tradedate_str = str(last_tradedate)
        return last_tradedate_str
