
import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QMessageBox, QFormLayout, QSpinBox, 
    QDoubleSpinBox, QDialog, QHeaderView, QTextEdit, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
from database import init_db
from localization import get_text
from models import WarehouseModel

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODERN_QSS = """
QMainWindow {
    background-color: #f3f4f6;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
/* سایدبار کناری */
QWidget#sidebar {
    background-color: #1e1b4b;
    border-top-left-radius: 12px;
    border-bottom-left-radius: 12px;
}
QPushButton.nav_btn {
    background-color: transparent;
    color: #c7d2fe;
    text-align: right;
    padding: 12px 20px;
    border: none;
    font-size: 14px;
    font-weight: bold;
    border-radius: 8px;
    margin: 4px 10px;
}
QPushButton.nav_btn:hover {
    background-color: #312e81;
    color: #ffffff;
}
QPushButton.nav_btn:checked {
    background-color: #4f46e5;
    color: #ffffff;
}
/* استایل دکمه‌های عمومی */
QPushButton {
    background-color: #4f46e5;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #4338ca;
}
QPushButton#btn_danger {
    background-color: #ef4444;
}
QPushButton#btn_danger:hover {
    background-color: #dc2626;
}
QPushButton#btn_success {
    background-color: #10b981;
}
QPushButton#btn_success:hover {
    background-color: #059669;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    padding: 10px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    background: #ffffff;
    font-size: 13px;
    color: #1f2937;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #4f46e5;
}
QTableWidget {
    gridline-color: #f3f4f6;
    background-color: #ffffff;
    selection-background-color: #e0e7ff;
    selection-color: #1e1b4b;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
}
QHeaderView::section {
    background-color: #f9fafb;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #e5e7eb;
    font-weight: bold;
    color: #374151;
    font-size: 13px;
}
QCheckBox {
    font-weight: bold;
    color: #374151;
    spacing: 8px;
}
"""

class LoginDialog(QDialog):
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.setWindowTitle(get_text("login_title", self.lang))
        self.resize(400, 240)
        self.setStyleSheet(MODERN_QSS)
        
        if self.lang == "fa":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        layout = QFormLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title_lbl = QLabel(get_text("login_title", self.lang))
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #4f46e5; margin-bottom: 10px;")
        layout.addRow(title_lbl)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("admin / worker")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.returnPressed.connect(self.handle_login)

        layout.addRow(get_text("username", self.lang), self.user_input)
        layout.addRow(get_text("password", self.lang), self.pass_input)

        self.btn_login = QPushButton(get_text("login_btn", self.lang))
        self.btn_login.clicked.connect(self.handle_login)
        layout.addRow(self.btn_login)

        self.user_data = None

    def handle_login(self):
        u = self.user_input.text().strip()
        p = self.pass_input.text().strip()
        
        if not u or not p:
            QMessageBox.warning(self, get_text("error", self.lang), "نام کاربری و رمز عبور نمی‌تواند خالی باشد.")
            return

        try:
            user = WarehouseModel.authenticate(u, p)
            if user:
                self.user_data = user
                self.accept()
            else:
                QMessageBox.warning(self, get_text("error", self.lang), get_text("login_error", self.lang))
        except Exception as e:
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ارتباط با پایگاه داده: {str(e)}")


class ProductDetailsDialog(QDialog):
    def __init__(self, prod_id, lang):
        super().__init__()
        self.lang = lang
        self.prod_id = prod_id
        self.setWindowTitle(get_text("product_details", self.lang))
        self.resize(600, 500)
        self.setStyleSheet(MODERN_QSS)

        if self.lang == "fa":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        product = WarehouseModel.get_product_by_id(prod_id)
        if not product:
            return

        # اطلاعات محصول و تامین‌کننده
        toman = get_text("toman", self.lang)
        info_html = f"""
        <h3 style='color: #4f46e5; margin-bottom: 10px;'>📦 {product[2]} (SKU: {product[1]})</h3>
        <table width='100%' cellpadding='8' style='background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;'>
            <tr>
                <td><b>{get_text('category', self.lang)}:</b> {product[3] or '-'}</td>
                <td><b>{get_text('price', self.lang)}:</b> {product[4]:,.0f} {toman}</td>
            </tr>
            <tr>
                <td><b>{get_text('quantity', self.lang)}:</b> {product[5]}</td>
                <td><b>{get_text('supplier', self.lang)}:</b> {product[6] or '-'} ({product[7] or 'بدون تلفن'})</td>
            </tr>
        </table>
        <h4 style='margin-top: 15px; color: #1e293b;'>تاریخچه تراکنش‌های این کالا:</h4>
        """
        lbl_info = QLabel(info_html)
        layout.addWidget(lbl_info)

        # جدول تراکنش‌های کالا
        self.table_trans = QTableWidget()
        self.table_trans.setColumnCount(4)
        self.table_trans.setHorizontalHeaderLabels(["نوع", "تعداد", "تاریخ", "توضیحات"])
        self.table_trans.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_trans)

        trans_rows = WarehouseModel.get_product_transactions(prod_id)
        self.table_trans.setRowCount(len(trans_rows))
        for r_idx, r in enumerate(trans_rows):
            for c_idx, val in enumerate(r[1:]):
                self.table_trans.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))


class SmartWarehouseApp(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_id, self.username, self.role = user_info
        self.current_lang = WarehouseModel.get_setting("language") or "fa"
        
        role_title = "مدیر سیستم (Admin)" if self.role == 'admin' else "انباردار (Worker)"
        self.setWindowTitle(f"{get_text('app_title', self.current_lang)} | کاربر: {self.username} [{role_title}]")
        self.resize(1300, 800)
        self.setStyleSheet(MODERN_QSS)
        
        if self.current_lang == "fa":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- منوی کناری (Sidebar) ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 20, 5, 20)
        sidebar_layout.setSpacing(8)

        logo_lbl = QLabel("🏢 STWE Warehouse")
        logo_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 10px 15px; margin-bottom: 15px;")
        sidebar_layout.addWidget(logo_lbl)

        self.nav_buttons = []
        nav_items = [
            (get_text("dashboard", self.current_lang), 0),
            (get_text("products", self.current_lang), 1),
            (get_text("categories", self.current_lang), 2),
            (get_text("suppliers", self.current_lang), 3),
            (get_text("transactions", self.current_lang), 4),
            (get_text("reports", self.current_lang), 5),
            (get_text("settings", self.current_lang), 6),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("nav_btn")
            btn.setProperty("class", "nav_btn")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # --- صفحات اصلی (Stacked Widget) ---
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.page_dashboard = QWidget()
        self.page_products = QWidget()
        self.page_categories = QWidget()
        self.page_suppliers = QWidget()
        self.page_transactions = QWidget()
        self.page_reports = QWidget()
        self.page_settings = QWidget()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_products)
        self.stack.addWidget(self.page_categories)
        self.stack.addWidget(self.page_suppliers)
        self.stack.addWidget(self.page_transactions)
        self.stack.addWidget(self.page_reports)
        self.stack.addWidget(self.page_settings)

        self.setup_dashboard_page()
        self.setup_products_page()
        self.setup_categories_page()
        self.setup_suppliers_page()
        self.setup_transactions_page()
        self.setup_reports_page()
        self.setup_settings_page()

        if self.role == 'warehouse':
            self.nav_buttons[2].setEnabled(False) # Categories
            self.nav_buttons[3].setEnabled(False) # Suppliers
            self.nav_buttons[6].setEnabled(False) # Settings

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for idx, btn in enumerate(self.nav_buttons):
            btn.setChecked(idx == index)
        if index == 0:
            self.update_dashboard_stats()

    def setup_dashboard_page(self):
        layout = QVBoxLayout(self.page_dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        self.lbl_stats = QLabel()
        self.lbl_stats.setStyleSheet("background: transparent;")
        self.update_dashboard_stats()
        layout.addWidget(self.lbl_stats)
        layout.addStretch()

    def update_dashboard_stats(self):
        stats = WarehouseModel.get_dashboard_stats()
        toman_label = get_text("toman", self.current_lang)
        text = f"""
        <h2 style='color: #1e1b4b; margin-bottom: 20px; font-weight: 700;'>🚀 {get_text('dashboard', self.current_lang)}</h2>
        <table width='100%' cellpadding='15' cellspacing='15'>
            <tr>
                <td style='background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px;'>
                    <h4 style='color: #1e40af; margin: 0 0 5px 0;'>📦 {get_text('total_products', self.current_lang)}</h4>
                    <span style='font-size: 26px; font-weight: bold; color: #1d4ed8;'>{stats['total_products']}</span>
                </td>
                <td style='background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px;'>
                    <h4 style='color: #065f46; margin: 0 0 5px 0;'>📊 {get_text('total_units', self.current_lang)}</h4>
                    <span style='font-size: 26px; font-weight: bold; color: #047857;'>{stats['total_units']}</span>
                </td>
            </tr>
            <tr>
                <td style='background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px;'>
                    <h4 style='color: #991b1b; margin: 0 0 5px 0;'>⚠️ {get_text('low_stock_count', self.current_lang)}</h4>
                    <span style='font-size: 26px; font-weight: bold; color: #dc2626;'>{stats['low_stock_count']}</span>
                </td>
                <td style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;'>
                    <h4 style='color: #166534; margin: 0 0 5px 0;'>💰 {get_text('total_inventory_value', self.current_lang)}</h4>
                    <span style='font-size: 26px; font-weight: bold; color: #15803d;'>{stats['total_value']:,.0f} {toman_label}</span>
                </td>
            </tr>
        </table>
        """
        self.lbl_stats.setText(text)

    def setup_products_page(self):
        layout = QVBoxLayout(self.page_products)
        layout.setContentsMargins(20, 20, 20, 20)

        h_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText(get_text("search", self.current_lang))
        self.txt_search.textChanged.connect(self.load_products_table)
        h_layout.addWidget(self.txt_search)

        self.chk_low_stock = QCheckBox(get_text("filter_low_stock", self.current_lang))
        self.chk_low_stock.stateChanged.connect(self.load_products_table)
        h_layout.addWidget(self.chk_low_stock)

        if self.role == 'admin':
            btn_add = QPushButton(get_text("add_product", self.current_lang))
            btn_add.clicked.connect(self.open_add_product_dialog)
            h_layout.addWidget(btn_add)
        
        btn_in = QPushButton(get_text("stock_in", self.current_lang))
        btn_in.setObjectName("btn_success")
        btn_in.clicked.connect(lambda: self.open_stock_movement_dialog('IN'))
        h_layout.addWidget(btn_in)

        btn_out = QPushButton(get_text("stock_out", self.current_lang))
        btn_out.setObjectName("btn_danger")
        btn_out.clicked.connect(lambda: self.open_stock_movement_dialog('OUT'))
        h_layout.addWidget(btn_out)

        layout.addLayout(h_layout)

        self.table_products = QTableWidget()
        self.table_products.setColumnCount(7)
        self.table_products.setHorizontalHeaderLabels(["ID", "SKU", get_text("name", self.current_lang), get_text("category", self.current_lang), get_text("price", self.current_lang), get_text("quantity", self.current_lang), get_text("supplier", self.current_lang)])
        self.table_products.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_products.doubleClicked.connect(self.open_product_details)
        layout.addWidget(self.table_products)
        self.load_products_table()

    def load_products_table(self):
        query = self.txt_search.text()
        low_only = self.chk_low_stock.isChecked()
        rows = WarehouseModel.get_all_products(query, low_only)
        self.table_products.setRowCount(len(rows))
        toman = get_text("toman", self.current_lang)
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row[:7]):
                item_text = str(val) if val is not None else "-"
                if c_idx == 4:
                    try:
                        item_text = f"{float(val):,.0f} {toman}"
                    except:
                        pass
                self.table_products.setItem(r_idx, c_idx, QTableWidgetItem(item_text))

    def open_product_details(self, index):
        row = index.row()
        prod_id = int(self.table_products.item(row, 0).text())
        dlg = ProductDetailsDialog(prod_id, self.current_lang)
        dlg.exec()

    def open_add_product_dialog(self):
        if self.role != 'admin':
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(get_text("add_product", self.current_lang))
        dlg.resize(420, 380)
        dlg.setStyleSheet(MODERN_QSS)
        form = QFormLayout(dlg)
        form.setContentsMargins(25, 25, 25, 25)

        sku_input = QLineEdit()
        name_input = QLineEdit()
        
        cat_combo = QComboBox()
        categories = WarehouseModel.get_all_categories()
        for c in categories:
            cat_combo.addItem(c[1], c[0])

        price_input = QDoubleSpinBox()
        price_input.setMaximum(10000000000)
        qty_input = QSpinBox()
        qty_input.setMaximum(1000000)

        sup_combo = QComboBox()
        suppliers = WarehouseModel.get_all_suppliers()
        sup_combo.addItem("---", None)
        for s in suppliers:
            sup_combo.addItem(s[1], s[0])

        form.addRow("SKU:", sku_input)
        form.addRow(get_text("name", self.current_lang), name_input)
        form.addRow(get_text("category", self.current_lang), cat_combo)
        form.addRow(get_text("price", self.current_lang), price_input)
        form.addRow(get_text("quantity", self.current_lang), qty_input)
        form.addRow(get_text("supplier", self.current_lang), sup_combo)

        btn_save = QPushButton(get_text("save", self.current_lang))
        form.addRow(btn_save)

        def save_action():
            if not cat_combo.currentData():
                QMessageBox.warning(dlg, get_text("warning", self.current_lang), "Please select a category first.")
                return
            success, err = WarehouseModel.add_product(
                sku_input.text(), name_input.text(), cat_combo.currentData(),
                price_input.value(), qty_input.value(), sup_combo.currentData()
            )
            if success:
                QMessageBox.information(dlg, get_text("success", self.current_lang), "Product added successfully!")
                dlg.accept()
                self.load_products_table()
                self.update_dashboard_stats()
            else:
                QMessageBox.warning(dlg, get_text("error", self.current_lang), get_text(err, self.current_lang))

        btn_save.clicked.connect(save_action)
        dlg.exec()

    def open_stock_movement_dialog(self, m_type):
        selected_items = self.table_products.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, get_text("warning", self.current_lang), "Please select a product first.")
            return
        
        row = selected_items[0].row()
        prod_id = int(self.table_products.item(row, 0).text())
        prod_name = self.table_products.item(row, 2).text()

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{get_text('stock_in' if m_type=='IN' else 'stock_out', self.current_lang)} - {prod_name}")
        dlg.resize(380, 220)
        dlg.setStyleSheet(MODERN_QSS)
        form = QFormLayout(dlg)
        form.setContentsMargins(25, 25, 25, 25)

        qty_input = QSpinBox()
        qty_input.setMaximum(100000)
        note_input = QLineEdit()

        form.addRow(get_text("quantity", self.current_lang), qty_input)
        form.addRow(get_text("description", self.current_lang), note_input)

        btn_save = QPushButton(get_text("save", self.current_lang))
        form.addRow(btn_save)

        def save_movement():
            success, err = WarehouseModel.stock_movement(prod_id, m_type, qty_input.value(), note_input.text())
            if success:
                QMessageBox.information(dlg, get_text("success", self.current_lang), "Transaction recorded successfully!")
                dlg.accept()
                self.load_products_table()
                self.load_transactions_table()
                self.update_dashboard_stats()
            else:
                QMessageBox.warning(dlg, get_text("error", self.current_lang), get_text(err, self.current_lang))

        btn_save.clicked.connect(save_movement)
        dlg.exec()

    def setup_categories_page(self):
        layout = QVBoxLayout(self.page_categories)
        layout.setContentsMargins(20, 20, 20, 20)

        h_layout = QHBoxLayout()
        self.cat_name_input = QLineEdit()
        self.cat_name_input.setPlaceholderText(get_text("category", self.current_lang))
        h_layout.addWidget(self.cat_name_input)

        btn_add_cat = QPushButton(get_text("add_category", self.current_lang))
        btn_add_cat.clicked.connect(self.add_category_action)
        h_layout.addWidget(btn_add_cat)
        h_layout.addStretch()
        layout.addLayout(h_layout)

        self.table_categories = QTableWidget()
        self.table_categories.setColumnCount(2)
        self.table_categories.setHorizontalHeaderLabels(["ID", get_text("name", self.current_lang)])
        self.table_categories.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_categories)
        self.load_categories_table()

    def load_categories_table(self):
        rows = WarehouseModel.get_all_categories()
        self.table_categories.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                self.table_categories.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))

    def add_category_action(self):
        name = self.cat_name_input.text().strip()
        if not name:
            return
        if WarehouseModel.add_category(name):
            self.cat_name_input.clear()
            self.load_categories_table()
            QMessageBox.information(self, get_text("success", self.current_lang), "Category added successfully!")
        else:
            QMessageBox.warning(self, get_text("error", self.current_lang), "Category already exists!")

    def setup_suppliers_page(self):
        layout = QVBoxLayout(self.page_suppliers)
        layout.setContentsMargins(20, 20, 20, 20)

        h_layout = QHBoxLayout()
        btn_add_sup = QPushButton(get_text("add_supplier", self.current_lang))
        btn_add_sup.clicked.connect(self.open_add_supplier_dialog)
        h_layout.addWidget(btn_add_sup)
        h_layout.addStretch()
        layout.addLayout(h_layout)

        self.table_suppliers = QTableWidget()
        self.table_suppliers.setColumnCount(7)
        self.table_suppliers.setHorizontalHeaderLabels(["ID", get_text("name", self.current_lang), get_text("phone", self.current_lang), get_text("email", self.current_lang), get_text("address", self.current_lang), get_text("description", self.current_lang), get_text("products_count", self.current_lang)])
        self.table_suppliers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_suppliers)
        self.load_suppliers_table()

    def load_suppliers_table(self):
        rows = WarehouseModel.get_all_suppliers()
        self.table_suppliers.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                self.table_suppliers.setItem(r_idx, c_idx, QTableWidgetItem(str(val) if val is not None else ""))

    def open_add_supplier_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(get_text("add_supplier", self.current_lang))
        dlg.resize(400, 420)
        dlg.setStyleSheet(MODERN_QSS)
        form = QFormLayout(dlg)
        form.setContentsMargins(25, 25, 25, 25)

        name_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        address_input = QLineEdit()
        desc_input = QTextEdit()

        form.addRow(get_text("name", self.current_lang), name_input)
        form.addRow(get_text("phone", self.current_lang), phone_input)
        form.addRow(get_text("email", self.current_lang), email_input)
        form.addRow(get_text("address", self.current_lang), address_input)
        form.addRow(get_text("description", self.current_lang), desc_input)

        btn_save = QPushButton(get_text("save", self.current_lang))
        form.addRow(btn_save)

        def save_sup():
            if not name_input.text().strip():
                return
            WarehouseModel.add_supplier(name_input.text(), phone_input.text(), email_input.text(), address_input.text(), desc_input.toPlainText())
            QMessageBox.information(dlg, get_text("success", self.current_lang), "Supplier added successfully!")
            dlg.accept()
            self.load_suppliers_table()

        btn_save.clicked.connect(save_sup)
        dlg.exec()

    def setup_transactions_page(self):
        layout = QVBoxLayout(self.page_transactions)
        layout.setContentsMargins(20, 20, 20, 20)

        self.table_transactions = QTableWidget()
        self.table_transactions.setColumnCount(7)
        self.table_transactions.setHorizontalHeaderLabels(["ID", "SKU", get_text("name", self.current_lang), "Type", get_text("quantity", self.current_lang), "Date", get_text("description", self.current_lang)])
        self.table_transactions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_transactions)
        self.load_transactions_table()

    def load_transactions_table(self):
        rows = WarehouseModel.get_all_transactions()
        self.table_transactions.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                self.table_transactions.setItem(r_idx, c_idx, QTableWidgetItem(str(val) if val is not None else ""))

    def setup_reports_page(self):
        layout = QVBoxLayout(self.page_reports)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        lbl_info = QLabel("<b>مرکز گزارش‌گیری و خروجی‌های هوشمند سیستم</b>")
        lbl_info.setStyleSheet("font-size: 15px; color: #374151; margin-bottom: 10px;")
        layout.addWidget(lbl_info)

        btn_pdf_prod = QPushButton(get_text("report_products_pdf", self.current_lang))
        btn_pdf_prod.setObjectName("btn_danger")
        btn_pdf_prod.clicked.connect(self.export_products_pdf)
        layout.addWidget(btn_pdf_prod)

        btn_pdf_trans = QPushButton(get_text("report_transactions_pdf", self.current_lang))
        btn_pdf_trans.setObjectName("btn_danger")
        btn_pdf_trans.clicked.connect(self.export_transactions_pdf)
        layout.addWidget(btn_pdf_trans)

        btn_excel = QPushButton(get_text("export_excel", self.current_lang))
        btn_excel.setObjectName("btn_success")
        btn_excel.clicked.connect(self.export_to_excel)
        layout.addWidget(btn_excel)

        btn_chart = QPushButton(get_text("save_chart", self.current_lang))
        btn_chart.clicked.connect(self.generate_bar_chart)
        layout.addWidget(btn_chart)

        layout.addStretch()

    def export_products_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "products_report.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return
        
        rows = WarehouseModel.get_all_products()
        html = "<h2>Smart Warehouse - Products Report</h2><table border='1' cellspacing='0' cellpadding='6' width='100%'>"
        html += "<tr style='background:#f3f4f6;'><th>SKU</th><th>Name</th><th>Category</th><th>Price</th><th>Quantity</th></tr>"
        for r in rows:
            html += f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]:,.0f}</td><td>{r[5]}</td></tr>"
        html += "</table>"

        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        doc.print_(printer)
        QMessageBox.information(self, get_text("success", self.current_lang), "Products PDF exported successfully!")

    def export_transactions_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "transactions_report.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return
        
        rows = WarehouseModel.get_all_transactions()
        html = "<h2>Smart Warehouse - Transactions Report</h2><table border='1' cellspacing='0' cellpadding='6' width='100%'>"
        html += "<tr style='background:#f3f4f6;'><th>SKU</th><th>Product Name</th><th>Type</th><th>Qty</th><th>Date</th><th>Note</th></tr>"
        for r in rows:
            html += f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td></tr>"
        html += "</table>"

        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        doc.print_(printer)
        QMessageBox.information(self, get_text("success", self.current_lang), "Transactions PDF exported successfully!")

    def generate_bar_chart(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "stock_chart.png", "Images (*.png)")
        if not file_path:
            return
        
        rows = WarehouseModel.get_all_products()
        if not rows:
            return
        names = [row[2] for row in rows[:10]]
        quantities = [row[5] for row in rows[:10]]

        plt.figure(figsize=(9, 5))
        plt.bar(names, quantities, color='#4f46e5', width=0.6)
        plt.xlabel('Products', fontsize=12)
        plt.ylabel('Quantity', fontsize=12)
        plt.title('Top Products Stock Quantity', fontsize=14, fontweight='bold', color='#1e1b4b')
        plt.xticks(rotation=25, ha='right')
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        QMessageBox.information(self, get_text("success", self.current_lang), "Chart saved successfully!")

    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "warehouse_report.xlsx", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        rows = WarehouseModel.get_all_products()
        if not rows:
            return
        df = pd.DataFrame(rows, columns=["ID", "SKU", "Name", "Category", "Price", "Quantity", "Supplier", "Supplier ID", "Cat ID"])
        df.to_excel(file_path, index=False)
        QMessageBox.information(self, get_text("success", self.current_lang), "Report exported to Excel successfully!")

    def setup_settings_page(self):
        layout = QFormLayout(self.page_settings)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("فارسی (Persian)", "fa")
        self.lang_combo.addItem("English", "en")
        current_lang_val = WarehouseModel.get_setting("language")
        self.lang_combo.setCurrentIndex(0 if current_lang_val == "fa" else 1)

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMaximum(1000)
        current_threshold = int(WarehouseModel.get_setting("low_stock_threshold") or 5)
        self.threshold_spin.setValue(current_threshold)

        btn_save_settings = QPushButton(get_text("save", self.current_lang))
        btn_save_settings.clicked.connect(self.save_settings)

        # دکمه‌های پشتیبان‌گیری و بازیابی
        btn_backup = QPushButton(get_text("backup_db", self.current_lang))
        btn_backup.setObjectName("btn_success")
        btn_backup.clicked.connect(self.backup_action)

        btn_restore = QPushButton(get_text("restore_db", self.current_lang))
        btn_restore.setObjectName("btn_danger")
        btn_restore.clicked.connect(self.restore_action)

        layout.addRow(get_text("language", self.current_lang), self.lang_combo)
        layout.addRow(get_text("threshold", self.current_lang), self.threshold_spin)
        layout.addRow(btn_save_settings)
        layout.addRow(QLabel("<hr style='border: 1px solid #e5e7eb;'>"))
        layout.addRow(btn_backup)
        layout.addRow(btn_restore)

    def backup_action(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "stwe_backup.db", "Database Files (*.db)")
        if file_path:
            WarehouseModel.backup_database(file_path)
            QMessageBox.information(self, get_text("success", self.current_lang), get_text("backup_success", self.current_lang))

    def restore_action(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "Database Files (*.db)")
        if file_path:
            WarehouseModel.restore_database(file_path)
            QMessageBox.information(self, get_text("success", self.current_lang), get_text("restore_success", self.current_lang))
            python = sys.executable
            import os
            os.execl(python, python, *sys.argv)

    def save_settings(self):
        selected_lang = self.lang_combo.currentData()
        threshold_val = self.threshold_spin.value()
        
        WarehouseModel.set_setting("language", selected_lang)
        WarehouseModel.set_setting("low_stock_threshold", threshold_val)
        
        QMessageBox.information(self, get_text("success", self.current_lang), "Settings saved. Restarting application...")
        python = sys.executable
        import os
        os.execl(python, python, *sys.argv)
