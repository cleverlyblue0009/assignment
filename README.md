# Analytics Dashboard - Streamlit + SQLite

A fully working local analytics dashboard built with Streamlit and SQLite.

## Features

- **Multi-select filters** for Legal Entity and Partner Entity
- **Dependent filtering**: Partner options update based on selected Legal Entities
- **Reactive metrics**: Total records, sales, average, and quantity
- **5 interactive charts**: Bar, pie, line, and horizontal bar charts
- **Data table**: Full filtered dataset at the bottom
- **Clean layout**: Filters → Metrics → Charts → Data Table

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database

Creates `analytics.db` with sample data (50 transactions):
```bash
python init_db.py
```

### 3. Run the Dashboard
```bash
streamlit run streamlit_dashboard.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

- **init_db.py**: Creates SQLite database and populates it with 50 sample transactions
- **streamlit_dashboard.py**: Streamlit app that queries the database and displays interactive analytics
- **analytics.db**: SQLite database file (created automatically by init_db.py)

## Database Schema
```
transactions table:
- id (INTEGER, primary key)
- legal_entity (TEXT)
- partner_entity (TEXT)
- sales_amount (REAL)
- transaction_date (TEXT)
- quantity (INTEGER)
- region (TEXT)
```

## Usage

1. Use the **Legal Entity** filter to select one or more entities
2. Use the **Partner Entity** filter to further refine (options update automatically)
3. View updated **metrics** and **charts** based on your selections
4. Scroll down to see the **full data table** with all matching records
5. Click **"Show Analytics"** to toggle charts on/off

## Notes

- All filtering happens at the database level (SQL queries), not in pandas
- Charts and metrics are reactive — they update instantly when filters change
- The database includes 50 sample transactions spanning January 2024