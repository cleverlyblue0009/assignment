

import sqlite3
from datetime import datetime, timedelta
import random

DB_FILE = "analytics.db"

def init_database():
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legal_entity TEXT NOT NULL,
            partner_entity TEXT NOT NULL,
            sales_amount REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            region TEXT NOT NULL
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] > 0:
        print(f"Database {DB_FILE} already populated. Skipping data insertion.")
        conn.close()
        return
    
  
    legal_entities = ['Entity A', 'Entity B', 'Entity C']
    partner_entities = ['Partner 1', 'Partner 2', 'Partner 3', 'Partner 4']
    regions = ['North', 'South', 'East', 'West']
    
    base_date = datetime(2024, 1, 1)
    transactions = []
    
    for i in range(50):
        legal_entity = random.choice(legal_entities)
        partner_entity = random.choice(partner_entities)
        sales_amount = round(random.uniform(500, 5000), 2)
        transaction_date = base_date + timedelta(days=i)
        quantity = random.randint(5, 100)
        region = random.choice(regions)
        
        transactions.append((
            legal_entity,
            partner_entity,
            sales_amount,
            transaction_date.strftime('%Y-%m-%d'),
            quantity,
            region
        ))
    
    cursor.executemany('''
        INSERT INTO transactions 
        (legal_entity, partner_entity, sales_amount, transaction_date, quantity, region)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', transactions)
    
    conn.commit()
    conn.close()
    
    print(f" Database initialized: {DB_FILE}")
    print(f" Created transactions table with {len(transactions)} sample records")

if __name__ == "__main__":
    init_database()