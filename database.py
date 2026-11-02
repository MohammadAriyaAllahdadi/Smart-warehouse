import sqlite3
import hashlib

DB_NAME = "stwe_warehouse.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ساخت جدول تنظیمات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # ساخت جدول دسته‌بندی‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # ساخت جدول کاربران
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # ساخت جدول تامین‌کنندگان
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            description TEXT
        )
    """)

    # ساخت جدول محصولات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            supplier_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
    """)

    # ساخت جدول تراکنش‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            sku TEXT,
            product_name TEXT,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    # درج تنظیمات پیش‌فرض
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('language', 'fa')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('low_stock_threshold', '5')")

    # ساخت کاربران پیش‌فرض (admin و worker)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin123'), 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('worker', hash_password('worker123'), 'warehouse'))

    conn.commit()
    conn.close()

# اجرای خودکار تابع ساخت دیتابیس به محض ایمپورت شدن این فایل
init_db()

if __name__ == "__main__":
    init_db()
