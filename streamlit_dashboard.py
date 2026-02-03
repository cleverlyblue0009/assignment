

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Tuple


DB_FILE = "analytics.db"

def get_connection():
    """Get SQLite connection."""
    return sqlite3.connect(DB_FILE)

def execute_query(query: str, params: Tuple = ()) -> pd.DataFrame:
    """Execute query and return results as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .filter-container { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    .metrics-container { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)


if 'selected_legal_entities' not in st.session_state:
    st.session_state.selected_legal_entities = []

if 'selected_partner_entities' not in st.session_state:
    st.session_state.selected_partner_entities = []

if 'show_analytics' not in st.session_state:
    st.session_state.show_analytics = False


def get_all_legal_entities() -> List[str]:
    """Get all unique legal entities from database."""
    query = "SELECT DISTINCT legal_entity FROM transactions ORDER BY legal_entity"
    df = execute_query(query)
    return df['legal_entity'].tolist()

def get_partner_entities_for_legal_entities(legal_entities: List[str]) -> List[str]:
    """Get partner entities for selected legal entities."""
    if not legal_entities:
        query = "SELECT DISTINCT partner_entity FROM transactions ORDER BY partner_entity"
        df = execute_query(query)
    else:
        # Use parameterized query with placeholders
        placeholders = ','.join(['?' for _ in legal_entities])
        query = f"SELECT DISTINCT partner_entity FROM transactions WHERE legal_entity IN ({placeholders}) ORDER BY partner_entity"
        df = execute_query(query, tuple(legal_entities))
    
    return df['partner_entity'].tolist()

def get_filtered_data(legal_entities: List[str] = None, partner_entities: List[str] = None) -> pd.DataFrame:
    """Get filtered data from database."""
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if legal_entities:
        placeholders = ','.join(['?' for _ in legal_entities])
        query += f" AND legal_entity IN ({placeholders})"
        params.extend(legal_entities)
    
    if partner_entities:
        placeholders = ','.join(['?' for _ in partner_entities])
        query += f" AND partner_entity IN ({placeholders})"
        params.extend(partner_entities)
    
    query += " ORDER BY transaction_date"
    
    return execute_query(query, tuple(params))


st.title("📊 Analytics Dashboard")
st.markdown("Real-time analytics with SQLite")
st.divider()


st.subheader("🔍 Filters")

filter_col1, filter_col2 = st.columns(2, gap="large")

# Filter 1: Legal Entity (Multi-select)
with filter_col1:
    st.markdown("**Legal Entity**")
    all_legal_entities = get_all_legal_entities()
    
    selected_legal_entities = st.multiselect(
        label="Select Legal Entity (or leave empty for all)",
        options=all_legal_entities,
        default=st.session_state.selected_legal_entities,
        key="legal_entity_filter",
        help="Select one or more legal entities"
    )
    st.session_state.selected_legal_entities = selected_legal_entities

# Filter 2: Partner Entity (Multi-select, dependent on Filter 1)
with filter_col2:
    st.markdown("**Partner Entity**")
    available_partners = get_partner_entities_for_legal_entities(
        st.session_state.selected_legal_entities
    )
    
    selected_partner_entities = st.multiselect(
        label="Select Partner Entity (or leave empty for all)",
        options=available_partners,
        default=st.session_state.selected_partner_entities,
        key="partner_entity_filter",
        help="Options update based on selected Legal Entities"
    )
    st.session_state.selected_partner_entities = selected_partner_entities

st.divider()

# ============================================================================
# GET FILTERED DATA (used by all sections below)
# ============================================================================

filtered_data = get_filtered_data(
    legal_entities=st.session_state.selected_legal_entities if st.session_state.selected_legal_entities else None,
    partner_entities=st.session_state.selected_partner_entities if st.session_state.selected_partner_entities else None
)

# ============================================================================
# SECTION 2: METRICS
# ============================================================================

st.subheader("📈 Summary Metrics")

total_records = len(filtered_data)
total_sales = filtered_data['sales_amount'].sum() if not filtered_data.empty else 0
avg_sales = filtered_data['sales_amount'].mean() if not filtered_data.empty else 0
total_quantity = filtered_data['quantity'].sum() if not filtered_data.empty else 0

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="medium")

with metric_col1:
    st.metric(label="Total Records", value=f"{total_records:,}")

with metric_col2:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")

with metric_col3:
    st.metric(label="Avg Sales", value=f"${avg_sales:,.2f}")

with metric_col4:
    st.metric(label="Total Quantity", value=f"{total_quantity:,.0f}")

st.divider()



st.subheader("📊 Analytics & Visualizations")

col_button = st.columns([2, 8])
with col_button[0]:
    if st.button("📈 Show Analytics", use_container_width=True, key="analytics_button"):
        st.session_state.show_analytics = not st.session_state.show_analytics

if st.session_state.show_analytics:
    st.info("📊 Charts reflect the currently applied filters")
    
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        st.subheader("Sales by Legal Entity")
        
        if not filtered_data.empty:
            sales_by_entity = filtered_data.groupby('legal_entity')['sales_amount'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sales_by_entity.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
            ax.set_title('Total Sales by Legal Entity', fontsize=12, fontweight='bold')
            ax.set_xlabel('Legal Entity', fontsize=10)
            ax.set_ylabel('Sales Amount ($)', fontsize=10)
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No data available")
    
    with chart_col2:
        st.subheader("Record Distribution by Partner")
        
        if not filtered_data.empty:
            partner_counts = filtered_data['partner_entity'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = sns.color_palette("husl", len(partner_counts))
            ax.pie(partner_counts, labels=partner_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax.set_title('Record Distribution by Partner Entity', fontsize=12, fontweight='bold')
            
            st.pyplot(fig)
        else:
            st.warning("No data available")
    
    chart_col3, chart_col4 = st.columns(2, gap="large")
    
    with chart_col3:
        st.subheader("Sales Trend Over Time")
        
        if not filtered_data.empty:
            sales_by_date = filtered_data.groupby('transaction_date')['sales_amount'].sum().sort_index()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(sales_by_date.index, sales_by_date.values, marker='o', 
                   linewidth=2, markersize=4, color='darkgreen')
            ax.fill_between(range(len(sales_by_date)), sales_by_date.values, alpha=0.3, color='green')
            ax.set_title('Sales Trend Over Time', fontsize=12, fontweight='bold')
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Sales Amount ($)', fontsize=10)
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.warning("No data available")
   
    with chart_col4:
        st.subheader("Quantity by Region")
        
        if not filtered_data.empty:
            qty_by_region = filtered_data.groupby('region')['quantity'].sum().sort_values(ascending=True)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            qty_by_region.plot(kind='barh', ax=ax, color='coral', edgecolor='black')
            ax.set_title('Total Quantity by Region', fontsize=12, fontweight='bold')
            ax.set_xlabel('Quantity', fontsize=10)
            ax.set_ylabel('Region', fontsize=10)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.warning("No data available")
    
    st.markdown("---")
    st.subheader("Top 10 Partner Entities by Sales")
    
    if not filtered_data.empty:
        top_partners = filtered_data.groupby('partner_entity')['sales_amount'].sum().nlargest(10).sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        top_partners.plot(kind='barh', ax=ax, color='mediumpurple', edgecolor='black')
        ax.set_title('Top 10 Partners by Sales Amount', fontsize=12, fontweight='bold')
        ax.set_xlabel('Sales Amount ($)', fontsize=10)
        ax.set_ylabel('Partner Entity', fontsize=10)
        plt.tight_layout()
        
        st.pyplot(fig)
    else:
        st.warning("No data available")

st.divider()


st.subheader("📋 Data Records")

st.markdown(f"Showing {len(filtered_data)} records")

if not filtered_data.empty:
    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True,
        height=400
    )
else:
    st.info("No records match the selected filters.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown(
    f"""
    <div style="text-align: center; color: #888; font-size: 12px;">
        <p>Analytics Dashboard | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Filters are reactive. All metrics and charts update automatically.</p>
    </div>
    """,
    unsafe_allow_html=True
)
