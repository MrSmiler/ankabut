
from settings_ui import Ui_Dialog
import ankabot_config as config
from PyQt5 import QtWidgets

class Settings(QtWidgets.QDialog , Ui_Dialog ):
    def __init__(self,parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.init_configs()
        self.reset_pb.clicked.connect(self.reset_button_clicked)
        self.save_pb.clicked.connect(self.save_button_clicked)
        self.cancel_pb.clicked.connect(self.cancel_button_clicked)
        self.extensionCategory_cb.currentIndexChanged.connect(self.extension_combo_changed)
        self.changeLanguage_cb.currentIndexChanged.connect(self.change_query_combos_changed)
        self.changeCategory_cb.currentIndexChanged.connect(self.change_query_combos_changed)
        if parent:
            self.parent = parent
    
    def init_configs(self):
        self.categories_dict = config.get_exts()
        self.extensionCategory_cb.clear()
        self.changeCategory_cb.clear()
        for key in self.categories_dict.keys():
            self.extensionCategory_cb.addItem(key)
            self.changeCategory_cb.addItem(key)
        ext = self.extensionCategory_cb.currentText()
        exts=self.categories_dict.get(ext)
        self.extensions_le.setText(' , '.join(exts))
        self.changeLanguage_cb.clear()
        for lang in config.get_langs():
            self.changeLanguage_cb.addItem(lang)
        lang = self.changeLanguage_cb.currentText()
        cat =  self.changeCategory_cb.currentText()
        query=config.get_query(lang , cat)
        self.changeQuery_le.setText(str(query))
        self.advancedQuery_le.setText(config.get_advanced_query())
        
        
    def reset_button_clicked(self):
        try:
            config.reset_data()
            self.init_configs()
            self.parent.init_lang_category() 
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,'Ankabot',str(e))

        else:
            QtWidgets.QMessageBox.information(self,'Ankabot','data was updated')

    def save_button_clicked(self):
        try:
            if self.addLanguage_rb.isChecked():
                lang=self.language_le.text()
                if not lang:
                    raise Exception('language can not be empty')
                config.add_lang(lang)

            #adds category
            elif self.addCategory_rb.isChecked():

                cat = self.newCategory_le.text()
                if not cat:
                    raise Exception('category can not be empty')
                config.add_category(cat)

            #changes the query for a specefic category and language
            elif self.changeQuery_rb.isChecked():
                cat = self.changeCategory_cb.currentText()
                lang = self.changeLanguage_cb.currentText()
                query = self.changeQuery_le.text()
                #add query
                config.change_query(lang,cat,query)
            elif self.addExtension_rb.isChecked():
                cat=self.extensionCategory_cb.currentText()
                exts=self.newExtension_le.text()
                if self.addExt_rb.isChecked():
                    exts = exts.split(',')
                    config.add_ext(cat ,exts)

                elif self.removeExt_rb.isChecked():
                    config.remove_ext(cat ,exts)
            elif self.changeAdvancedQuery_rb.isChecked():
                query=self.advancedQuery_le.text()
                config.change_advanced_query(query)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self,'Ankabot',str(e))

        else:
            QtWidgets.QMessageBox.information(self,'Ankabot','data was updated')
            self.init_configs()
            self.parent.init_lang_category() 

    
    def change_query_combos_changed(self):
        try:
            lang = self.changeLanguage_cb.currentText()
            cat = self.changeCategory_cb.currentText()
            query = config.get_query(lang,cat)

            self.changeQuery_le.setText(str(query))
        except Exception as e:
            QtWidgets.QMessageBox.information(self,'Ankabot',str(e))


        
    def extension_combo_changed(self):
        ext = self.extensionCategory_cb.currentText()
        exts= self.categories_dict.get(ext)
        try:
            self.extensions_le.setText(' , '.join(exts))
        except:
            pass
         




    def cancel_button_clicked(self):
        self.close()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec_())
