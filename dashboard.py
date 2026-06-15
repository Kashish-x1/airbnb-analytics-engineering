import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide"
)

# --------------------------------------------------
# SNOWFLAKE CONNECTION
# --------------------------------------------------

conn = snowflake.connector.connect(
    account="ZYWICWI-OF68525",
    user="ABHINAV",
    password="HGZH96qxCXudv42",
    warehouse="COMPUTE_WH",
    database="AIRBNB",
    schema="GOLD",
    role="ACCOUNTADMIN"
)

query = """
SELECT *
FROM OBT
"""

df = pd.read_sql(query, conn)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown("""
<div style="text-align:center;">

<img src="https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_Bélo.svg"
width="120">

<h1 style="margin-top:10px;">
Airbnb Analytics Dashboard
</h1>

<p style="font-size:20px; color:gray;">
End-to-End Data Engineering Pipeline using Snowflake, dbt & Streamlit
</p>

</div>
""", unsafe_allow_html=True)
st.success(
    "Built using AWS S3 • Snowflake • dbt • Streamlit Dashboard"
)

st.info("""
This dashboard is built using:

S3 → Snowflake → dbt (Bronze → Silver → Gold) → Streamlit

The dashboard uses the Gold Layer (OBT Model) as the final analytics-ready dataset.
""")

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

selected_country = st.sidebar.multiselect(
    "Select Country",
    sorted(df["COUNTRY"].dropna().unique()),
    default=sorted(df["COUNTRY"].dropna().unique())
)

selected_room = st.sidebar.multiselect(
    "Select Room Type",
    sorted(df["ROOM_TYPE"].dropna().unique()),
    default=sorted(df["ROOM_TYPE"].dropna().unique())
)

filtered_df = df[
    (df["COUNTRY"].isin(selected_country))
    &
    (df["ROOM_TYPE"].isin(selected_room))
]
st.sidebar.markdown("---")

st.sidebar.success("""
🏗️ Project Architecture

S3
↓
Snowflake
↓
Bronze Layer
↓
Silver Layer
↓
Gold Layer (OBT)
↓
Streamlit Dashboard
""")
# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📅 Total Bookings",
    len(filtered_df)
)

col2.metric(
    "👤 Total Hosts",
    filtered_df["HOST_ID"].nunique()
)

col3.metric(
    "🏠 Total Listings",
    filtered_df["LISTING_ID"].nunique()
)

col4.metric(
    "💰 Total Revenue",
    f"${filtered_df['TOTAL_AMOUNT'].sum():,.0f}"
)

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    ["📊 Business Overview",
     "👤 Host Analysis",
     "📋 Data Preview"]
)

# ==================================================
# TAB 1
# ==================================================

with tab1:

    c1, c2 = st.columns(2)

    with c1:

        property_chart = px.bar(
            filtered_df.groupby("PROPERTY_TYPE")["TOTAL_AMOUNT"]
            .sum()
            .reset_index(),
            x="PROPERTY_TYPE",
            y="TOTAL_AMOUNT",
            title="Revenue by Property Type"
        )

        st.plotly_chart(
            property_chart,
            use_container_width=True
        )

    with c2:

        booking_chart = px.pie(
           filtered_df,
           names="BOOKING_STATUS",
           title="Booking Status Distribution",
           hole=0.5
        )
        

        st.plotly_chart(
            booking_chart,
            use_container_width=True
        )

    c3, c4 = st.columns(2)

    with c3:

        country_chart = px.bar(
            filtered_df.groupby("COUNTRY")["TOTAL_AMOUNT"]
            .sum()
            .reset_index()
            .sort_values(
                "TOTAL_AMOUNT",
                ascending=False
            )
            .head(10),
            x="COUNTRY",
            y="TOTAL_AMOUNT",
            title="Top Countries by Revenue"
        )

        st.plotly_chart(
            country_chart,
            use_container_width=True
        )

    with c4:

        city_chart = px.bar(
            filtered_df.groupby("CITY")["TOTAL_AMOUNT"]
            .sum()
            .reset_index()
            .sort_values(
                "TOTAL_AMOUNT",
                ascending=False
            )
            .head(10),
            x="CITY",
            y="TOTAL_AMOUNT",
            title="Top Cities by Revenue"
        )

        st.plotly_chart(
            city_chart,
            use_container_width=True
        )
        st.subheader("🌍 Revenue Contribution by City")

revenue_city = (
    filtered_df
    .groupby("CITY")["TOTAL_AMOUNT"]
    .sum()
    .reset_index()
)

treemap_chart = px.treemap(
    revenue_city,
    path=["CITY"],
    values="TOTAL_AMOUNT",
    title="Revenue Contribution by City"
)

st.plotly_chart(
    treemap_chart,
    use_container_width=True
)

# ==================================================
# TAB 2
# ==================================================

with tab2:

    c5, c6 = st.columns(2)

    with c5:

        host_chart = px.bar(
            filtered_df["RESPONSE_RATE_QUALITY"]
            .value_counts()
            .reset_index(),
            x="RESPONSE_RATE_QUALITY",
            y="count",
            title="Host Quality Distribution"
        )

        st.plotly_chart(
            host_chart,
            use_container_width=True
        )

    with c6:

        superhost_chart = px.pie(
            filtered_df,
            names="IS_SUPERHOST",
            title="Superhost Distribution"
        )

        st.plotly_chart(
            superhost_chart,
            use_container_width=True
        )

    c7, c8 = st.columns(2)

    with c7:
        price_chart = px.pie(
            filtered_df,
            names="PRICE_PER_NIGHT_TAG",
            title="Price Category Distribution",
            hole=0.5
       )
        

        st.plotly_chart(
            price_chart,
            use_container_width=True
        )

    with c8:

        room_chart = px.bar(
            filtered_df["ROOM_TYPE"]
            .value_counts()
            .reset_index(),
            x="ROOM_TYPE",
            y="count",
            title="Room Type Distribution"
        )

        st.plotly_chart(
            room_chart,
            use_container_width=True
        )

# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.subheader("Gold Layer Data Preview")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )