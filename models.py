from database import get_connection, hash_password, DB_NAME
from datetime import datetime
import shutil

class WarehouseModel:
    @staticmethod
    def authenticate(username, password):
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, hashed))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_setting(key):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def set_setting(key, value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

    @staticmethod
    def get_dashboard_stats():
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(quantity), SUM(price * quantity) FROM products")
        res = cursor.fetchone()
        total_products = res[0] or 0
        total_units = res[1] or 0
        total_value = res[2] or 0.0

        threshold = int(WarehouseModel.get_setting("low_stock_threshold") or 5)
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= ?", (threshold,))
        low_stock_count = cursor.fetchone()[0] or 0

        conn.close()
        return {
            "total_products": total_products,
            "total_units": total_units,
            "total_value": total_value,
            "low_stock_count": low_stock_count
        }

    @staticmethod
    def get_all_products(search_query="", low_stock_only=False):
        conn = get_connection()
        cursor = conn.cursor()
        threshold = int(WarehouseModel.get_setting("low_stock_threshold") or 5)

        base_query = """
            SELECT p.id, p.sku, p.name, c.name, p.price, p.quantity, s.name, p.supplier_id, p.category_id
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
        """
        
        conditions = []
        params = []

        if search_query:
            conditions.append("(p.name LIKE ? OR p.sku LIKE ? OR c.name LIKE ?)")
            val = f"%{search_query}%"
            params.extend([val, val, val])

        if low_stock_only:
            conditions.append("p.quantity <= ?")
            params.append(threshold)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_product_by_id(prod_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.sku, p.name, c.name, p.price, p.quantity, s.name, s.phone, s.email, s.address
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = ?
        """, (prod_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_product_transactions(prod_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, quantity, date, note FROM transactions WHERE product_id = ? ORDER BY id DESC", (prod_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_product(sku, name, category_id, price, quantity, supplier_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO products (sku, name, category_id, price, quantity, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sku, name, category_id, price, quantity, supplier_id))
            prod_id = cursor.lastrowid
            if quantity > 0:
                cursor.execute("""
                    INSERT INTO transactions (product_id, sku, product_name, type, quantity, date, note)
                    VALUES (?, ?, ?, 'IN', ?, ?, 'Initial Stock')
                """, (prod_id, sku, name, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            return True, ""
        except Exception:
            return False, "duplicate_sku"
        finally:
            conn.close()

    @staticmethod
    def stock_movement(prod_id, movement_type, qty, note=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sku, name, quantity FROM products WHERE id = ?", (prod_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Product not found"
        
        sku, name, current_qty = row
        if movement_type == 'OUT' and current_qty < qty:
            conn.close()
            return False, "insufficient_stock"

        new_qty = current_qty + qty if movement_type == 'IN' else current_qty - qty
        cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_qty, prod_id))
        
        cursor.execute("""
            INSERT INTO transactions (product_id, sku, product_name, type, quantity, date, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (prod_id, sku, name, movement_type, qty, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), note))
        
        conn.commit()
        conn.close()
        return True, ""

    @staticmethod
    def get_all_categories():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_category(name):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_all_suppliers():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.phone, s.email, s.address, s.description, COUNT(p.id)
            FROM suppliers s LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.id
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_supplier(name, phone, email, address, description):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO suppliers (name, phone, email, address, description) VALUES (?, ?, ?, ?, ?)", 
                       (name, phone, email, address, description))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_transactions():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, sku, product_name, type, quantity, date, note FROM transactions ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def backup_database(dest_path):
        shutil.copyfile(DB_NAME, dest_path)

    @staticmethod
    def restore_database(source_path):
        shutil.copyfile(source_path, DB_NAME)
