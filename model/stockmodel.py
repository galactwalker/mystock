from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlTableModel


class StockTableModel:
    def __init__(self, db_conn_name, table_name, headers):
        self.model = self.createModel(db_conn_name, table_name, headers)

    def createModel(self, db_conn_name, table_name, headers):
        """Create and set up the model."""
        tableModel = QSqlTableModel(db=db_conn_name)
        tableModel.setTable(table_name)
        tableModel.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)   # 单元格变化
        tableModel.select()                                                     # 显示数据
        for columnIndex, header in enumerate(headers):
            tableModel.setHeaderData(columnIndex, Qt.Orientation.Horizontal, header)
        return tableModel

    def getDatas(self, index_list):             # index_list，List[QModelIndex]类型，是从tableview1中获取选中行的indexes，用来传递给tablemodel1获取选中行的数据
        # 遍历index_list，从tablemodel中获取相应的records数据，加入到一个List[QsqlRecord] 列表中
        records = []
        for model_index in index_list:
            records.append(self.model.record(model_index.row()))
            # QModelIndex.row() → int  Returns the row this model index refers to.
            # QSqlTableModel.record(int) → QSqlRecord  Returns the record at row in the model. If row is the index of a valid row, the record will be populated with values from that row.
        return records

    def getData(self, qModelIndex):             # QModelIndex类型，是从“预测预警”tableview中获取选中行的index，用来传递给tablemodel获取选中行的数据
        record = self.model.record(qModelIndex.row())
            # QModelIndex.row() → int  Returns the row number this model index refers to.
            # QSqlTableModel.record(int) → QSqlRecord  Returns the record at row in the model. If row is the index of a valid row, the record will be populated with values from that row.
        return record

    def receiveDatas(self, records):
        # 遍历List[QsqlRecord]列表，将数据传递给tablemodel表
        current_row = self.model.rowCount()
        for record in records:
            self.model.insertRecord(current_row, record)
        self.model.submitAll()
        # self.model.select() 加select，则数据更改后即时刷新，但不利于检查

    def deleteDatas(self, index_list):
        for model_index in index_list:
            self.model.removeRow(model_index.row())
        self.model.submitAll()
