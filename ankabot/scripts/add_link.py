
from add_link_ui import Ui_Dialog
from PyQt5 import QtWidgets


class AddLink(QtWidgets.QDialog , Ui_Dialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.downloadLink_pb.clicked.connect(self.download_button_clicked)
        self.cancelLink_pb.clicked.connect(self.close)
        if parent:
            self.parent = parent

    
    def download_button_clicked(self):
        url = self.newLink_le.text()
        self.parent.download_button_clicked(url)
        self.close()



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AddLink()
    window.show()
    sys.exit(app.exec_())
    



