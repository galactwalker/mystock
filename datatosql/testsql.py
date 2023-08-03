import sqlite3


class TestSqlite:

    def selectALL(self):
        conn = sqlite3.connect(r"D:\financeDB\SZ000009.sqlite")
        cur = conn.cursor()             # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        cur.execute("SELECT * FROM stksurv")
        print(cur.fetchall())

        conn.close()

    def create_talbe(self):
        conn = sqlite3.connect(r"D:\financeDB\StockRecycle.sqlite")
        cur = conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        cur.execute(
            "CREATE TABLE IF NOT EXISTS stockre (ts_code, symbol, name, area, industry, market, list_date, fullname, "
            "enname, cnspell, exchange, curr_type, list_status, is_hs, delist_date)")

        conn.close()

    def drop_table(self):
        conn = sqlite3.connect(r"D:\financeDB\SZ00063.sqlite")
        cur = conn.cursor()  # 一旦有了Connection对象，就可以创建一个Cursor对象。游标使我们能够对数据库执行SQL查询

        cur.execute("DROP TABLE hkhold")

        conn.close()

if __name__ == '__main__':
    test = TestSqlite()
    test.selectALL()
    #test.create_talbe()
    #test.drop_table()
