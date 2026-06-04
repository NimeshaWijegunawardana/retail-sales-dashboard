import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("📊 Retail Sales Analysis Dashboard")

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("Superstore.csv" , encoding='latin-1')

# -------------------------
# DATA CLEANING + FEATURE ENGINEERING
# -------------------------

# Convert date columns
df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

# Time features
df['Order Year'] = df['Order Date'].dt.year
df['Order Month'] = df['Order Date'].dt.month_name()

# Shipping days
df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days

# Profit margin
df['Profit Margin'] = df['Profit'] / df['Sales']
df['Profit Margin'] = df['Profit Margin'].replace([float('inf'), -float('inf')], 0)
df['Profit Margin'] = df['Profit Margin'].fillna(0)

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("🔎 Filters")

year = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df['Order Year'].unique()),
    default=sorted(df['Order Year'].unique())
)

region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

category = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Filter dataset
df_filtered = df[
    (df['Order Year'].isin(year)) &
    (df['Region'].isin(region)) &
    (df['Category'].isin(category))
]

# -------------------------
# KPI CARDS
# -------------------------
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
total_orders = df_filtered['Order ID'].nunique()
avg_margin = df_filtered['Profit Margin'].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Total Orders", total_orders)
col4.metric("Avg Profit Margin", f"{avg_margin:.2%}")

st.markdown("---")

# -------------------------
# SALES BY REGION
# -------------------------
region_sales = df_filtered.groupby('Region')['Sales'].sum().reset_index()

fig1 = px.bar(
    region_sales,
    x='Region',
    y='Sales',
    title="Sales by Region",
    text_auto=True
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# CATEGORY SALES
# -------------------------
category_sales = df_filtered.groupby('Category')['Sales'].sum().reset_index()

fig2 = px.pie(
    category_sales,
    names='Category',
    values='Sales',
    title="Sales by Category",
    hole=0.4
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# MONTHLY SALES TREND
# -------------------------
month_order = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
]

monthly_sales = df_filtered.groupby('Order Month')['Sales'].sum().reset_index()

monthly_sales['Order Month'] = pd.Categorical(
    monthly_sales['Order Month'],
    categories=month_order,
    ordered=True
)

monthly_sales = monthly_sales.sort_values('Order Month')

fig3 = px.line(
    monthly_sales,
    x='Order Month',
    y='Sales',
    markers=True,
    title="Monthly Sales Trend"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# TOP PRODUCTS
# -------------------------
top_products = (
    df_filtered.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x='Sales',
    y='Product Name',
    orientation='h',
    title="Top 10 Products by Sales"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# PROFIT VS DISCOUNT
# -------------------------
fig5 = px.scatter(
    df_filtered,
    x='Discount',
    y='Profit',
    color='Category',
    title="Profit vs Discount Relationship"
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------------
# SHIPPING ANALYSIS
# -------------------------
shipping = df_filtered.groupby('Ship Mode')['Shipping Days'].mean().reset_index()

fig6 = px.bar(
    shipping,
    x='Ship Mode',
    y='Shipping Days',
    title="Average Shipping Time by Ship Mode"
)

st.plotly_chart(fig6, use_container_width=True)