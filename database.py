import sqlite3

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
    def connect_db(self):
        conn = sqlite3.connect(self.db_name)
        return conn

    def check_if_user_exists(self, user_id):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        if user:
            return True
        return False

    def check_if_admin(self, user_id):
        return user_id == 1146337904

    def get_user_stocks(self, user_id):
        if self.check_if_user_exists(user_id):
            conn = self.connect_db()
            c = conn.cursor()
            c.execute('SELECT stock_symbol,quantity,average FROM user_stocks WHERE user_id = ?', (user_id,))
            stocks = c.fetchall()
            conn.close()
            return stocks
        else:
            return None
    
    def get_user_stock(self, user_id, stock):
        if self.check_if_user_exists(user_id):
            conn = self.connect_db()
            c = conn.cursor()
            c.execute('SELECT stock_symbol,quantity, average, id FROM user_stocks WHERE user_id = ? AND stock_symbol = ?', (user_id, stock))
            stock = c.fetchone()
            conn.close()
            return stock
        else:
            return None
    
    def get_transactions(self):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT * FROM transactions')
        transactions = c.fetchall()
        conn.close()
        return transactions


    def update_stock(self, user_id, stock, quantity,average_price):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('UPDATE user_stocks SET quantity = ?, average = ? WHERE user_id = ? AND stock_symbol = ?', (quantity,average_price,user_id,stock))
        conn.commit()
        conn.close()
    
    def add_transaction(self,stock_id, user_id, stock, quantity, price, date, transaction_type):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('INSERT INTO transactions (user_stock_id, user_id, stock_symbol, quantity, price, date, sell_or_buy) VALUES (?,?,?,?,?,?,?)', (stock_id, user_id, stock, quantity, price, date, transaction_type))
        conn.commit()
        conn.close()
    
    def add_stock(self,user_id, stock, quantity, average_price):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('INSERT INTO user_stocks (user_id, stock_symbol, quantity, average) VALUES (?,?,?,?)', (user_id, stock, quantity, average_price))
        conn.commit()
        conn.close()
    
    def delete_stock(self, user_id, stock):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('DELETE FROM user_stocks WHERE user_id = ? AND stock_symbol = ?', (user_id, stock))
        conn.commit()
        conn.close()