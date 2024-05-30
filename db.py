import sqlite3

class db:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def create_tables(self):
        create_users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            generated_id TEXT NOT NULL,
            username TEXT,
            registration_date TEXT
        );
        '''

        create_user_stocks_table = '''
        CREATE TABLE IF NOT EXISTS user_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stock_symbol TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            average REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        '''

        create_transactions_table = '''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_stock_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            stock_symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            sell_or_buy TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (user_stock_id) REFERENCES user_stocks(id)
        );
        '''

        self.c.execute(create_users_table)
        self.c.execute(create_user_stocks_table)
        self.c.execute(create_transactions_table)
        self.conn.commit()

    def close_connection(self):
        self.conn.close()