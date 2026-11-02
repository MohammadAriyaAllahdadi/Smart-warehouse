import sys
from PySide6.QtWidgets import QApplication
from localization import get_text
from models import WarehouseModel
from ui_main import LoginDialog, SmartWarehouseApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    current_lang = WarehouseModel.get_setting("language") or "fa"
    
    # نمایش فرم ورود
    login = LoginDialog(current_lang)
    if login.exec() == LoginDialog.Accepted and login.user_data:
        window = SmartWarehouseApp(login.user_data)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
