import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("https://raw.githubusercontent.com/mmhdagungg/e-commerce-public-data-analyst/refs/heads/main/dashboard/df.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Data Geolocation
geolocation = pd.read_csv("https://raw.githubusercontent.com/mmhdagungg/e-commerce-public-data-analyst/refs/heads/main/dashboard/geolocation.csv")
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9IOWpZQH2n_ybodBfjGbyzpLIzVez6LrGhQ&s"
                 , width=100)
    with col3:
        st.write(' ')

    # input date
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Judul
st.title("E-Commerce Data Analysis")

order_items_df = pd.read_csv("https://raw.githubusercontent.com/mmhdagungg/e-commerce-public-data-analyst/refs/heads/main/dashboard/df.csv")

sum_order_items_df = order_items_df.groupby('product_category_name_english').agg(
    product_count=('order_item_id', 'count')
).reset_index()

total_items = sum_order_items_df["product_count"].sum()
avg_items = sum_order_items_df["product_count"].mean()

st.markdown(f"**Total Items:** {total_items}")
st.markdown(f"**Rata-rata Items:** {avg_items}")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 10))

# Penjualan terbanyak
top_sales = sum_order_items_df.sort_values(by="product_count", ascending=False).head(5)
sns.barplot(x="product_count", y="product_category_name_english", 
            data=top_sales, palette="coolwarm", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=14)
ax[0].set_title("Penjualan Terbanyak", loc="center", fontsize=16)
ax[0].tick_params(axis='y', labelsize=12)
ax[0].tick_params(axis='x', labelsize=12)

# Penjualan terendah
sns.barplot(x="product_count", y="product_category_name_english", 
            data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="coolwarm", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=14)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Penjualan Terendah", loc="center", fontsize=16)
ax[1].tick_params(axis='y', labelsize=12)
ax[1].tick_params(axis='x', labelsize=12)

st.pyplot(fig)
with st.expander("Lihat Penjelasan"):
        st.write('Produk terlaris adalah bed_bath_table dan terendah adalah security dan services')

# Demografi Pelanggan
st.subheader("Demografi Pelanggan")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"State dengan customer terbanyak: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette="coolwarm"
                    )

    plt.title("Data Pelanggan berdasarkan State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Jumlah Pelanggan")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("Lihat Penjelasan"):
        st.write("Berdasarkan data, jumlah customer paling banyak berada di state SP (Sao Paulo) dan terendah berada di state RR (Roraima)")

with tab2:
    map_plot.plot()

    with st.expander("Lihat Penjelasan"):
        st.write('Pelanggan lebih banyak berada di Sao Paulo, Rio De Janiero, dll')