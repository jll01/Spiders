import sys
import pymysql

from jd import JD
from spider import Ui_Form
from PyQt5 import QtWidgets,QtCore
from PyQt5.Qt import QTableWidgetItem
from PyQt5.QtWidgets import QWidget, QMessageBox


class SpiderApp(Ui_Form, QWidget):
    def __init__(self):
        super(SpiderApp,self).__init__()
        self.connect = pymysql.connect(host='',user='',passwd='',port=0,db='')
        self.cur = self.connect.cursor()
        self.row_count = 0
        self.setFixedSize(self.width(), self.height())

    def get_inputshopname(self):
        return self.inputshopname.text()

    def get_threadnumber(self):
        try:
            return int(self.threadnumber.text())
        except:
            return 1

    def get_scope1(self):
        getdata = self.scope1.text()
        try:
            return int(getdata.strip())
        except Exception as e:
            return 0

    def get_scope2(self):
        getdata2 = self.scope2.text()
        try:
            return int(getdata2.strip())
        except Exception as e:
            return self.get_scope1()

    def run(self):
        name = self.get_inputshopname()
        thnum = self.get_threadnumber()
        spidernum = self.get_spiderpagenum()
        if len(name) == 0:
            QMessageBox.information(self, "警告！", "请重新输入商品名！", QMessageBox.Yes, QMessageBox.Yes)
        else:
            self.pagenumber.setText(str(spidernum))
            jd = JD(name, thnum)
            jd.get_data_from_mysql()
            jd.get_page_html(self.get_spiderpagenum())

    def find_data_fromsql(self):
        id1 = self.get_scope1()
        id2 = self.get_scope2()
        if id1 == 0 and id2 ==0:
            sql = 'select * from jd_shop'
        else:
            sql = 'select * from jd_shop where id>={} and id<={}'.format(id1,id2)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        row = self.cur.rowcount  # 取得记录个数，用于设置表格的行数
        vol = len(rows[0])  # 取得字段数，用于设置表格的列数

        self.datatable.setRowCount(row)

        for i in range(row):
            for j in range(1,vol):
                temp_data = rows[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.datatable.setItem(i, j-1, data)

    def shoppagenum(self):
        name = self.get_inputshopname()
        thnum = self.get_threadnumber()
        if len(name) == 0:
            QMessageBox.information(self, "警告！", "请重新输入商品名！", QMessageBox.Yes, QMessageBox.Yes)
        else:
            self.threadnumber.setText(str(thnum))
            jd = JD(name,thnum)
            pagenum = jd.get_shop_page_num()
            self.pagecount.setText(pagenum)

    def get_spiderpagenum(self):
        try:
            return int(self.pagenumber.text())
        except:
            return int(self.pagecount.text())


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    sa = SpiderApp()

    widget = QtWidgets.QWidget()
    sa.setupUi(widget)
    # SpiderApp.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

    widget.show()
    sa.runspider.clicked.connect(sa.run)
    sa.finddatafromsql.clicked.connect(sa.find_data_fromsql)
    sa.pagebutton.clicked.connect(sa.shoppagenum)
    # QMainWindow.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

    sys.exit(app.exec_())


