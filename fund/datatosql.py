import tushare as ts
# 初始化pro接口
pro = ts.pro_api('19574700f2ce77bbbc2bb9214c24045c88841297b481ac546b67f5cc')

# 拉取数据
df = pro.fund_basic(**{"ts_code": "",
    "market": "", "update_flag": "", "offset": "", "limit": "", "status": "", "name": ""
    }, fields=["ts_code", "name", "management", "custodian", "fund_type", "found_date", "due_date", "list_date",
    "issue_date", "delist_date", "issue_amount", "m_fee", "c_fee", "duration_year", "p_value", "min_amount",
    "exp_return", "benchmark", "status", "invest_type", "type", "trustee", "purc_startdate", "redm_startdate",
    "market"])
