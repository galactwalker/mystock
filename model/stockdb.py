from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox


class StockDBConnection:
    def __init__(self, database_name, connection_name):
        self.database = self.createConnection(database_name, connection_name)

    def createConnection(self, database_name, connection_name):
        connection = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        connection.setDatabaseName(database_name)
        return connection

    # 重写open()，增加自动报错（但因为setDatabaseName()会自动创建sqlite文件，所以似乎不好用）
    def open(self):
        if not self.database.open():
            QMessageBox.warning(
                None,
                "没找到",
                f"Database Error: {self.database.lastError().text()}",
            )
            return False
        return True
