# ============================================================
# Nassau Candy Distributor
# Factory-to-Customer Shipping Route Efficiency Dashboard
# ============================================================

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ------------------------------------------------------------
# 1. Dashboard configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy Shipping Analysis",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚚 Factory-to-Customer Shipping Route Analysis")
st.caption("Nassau Candy Distributor | Sales, routes, factories, and geography")

PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "outputs" / "cleaned_shipments.csv"


# ------------------------------------------------------------
# 2. Load and prepare data
# ------------------------------------------------------------
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    # Convert numeric fields safely
    numeric_columns = ["Sales", "Gross Profit", "Units", "Cost"]
    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    # Parse order dates for filtering
    if "Order Date" in data.columns:
        data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")

    return data


if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Run python analysis.py to generate outputs/cleaned_shipments.csv "
        "inside your project folder."
    )
    st.stop()

df = load_data(str(DATA_PATH))

required_columns = [
    "Order ID",
    "Order Date",
    "Ship Mode",
    "Region",
    "State/Province",
    "City",
    "Product Name",
    "Sales",
    "Gross Profit",
    "Units",
    "Ship Date",
    "Factory",
    "Shipping Lead Time",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()


# ------------------------------------------------------------
# 3. Product-to-factory mapping
# ------------------------------------------------------------
product_factory = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory",
}

df["Factory"] = df["Product Name"].map(product_factory)


# ------------------------------------------------------------
# 4. Factory coordinates from the project specification
# ------------------------------------------------------------
factory_locations = pd.DataFrame(
    [
        {
            "Factory": "Lot's O' Nuts",
            "Latitude": 32.881893,
            "Longitude": -111.768036,
        },
        {
            "Factory": "Wicked Choccy's",
            "Latitude": 32.076176,
            "Longitude": -81.088371,
        },
        {
            "Factory": "Sugar Shack",
            "Latitude": 48.119140,
            "Longitude": -96.181150,
        },
        {
            "Factory": "Secret Factory",
            "Latitude": 41.446333,
            "Longitude": -90.565487,
        },
        {
            "Factory": "The Other Factory",
            "Latitude": 35.117500,
            "Longitude": -89.971107,
        },
    ]
)


# ------------------------------------------------------------
# 5. Sidebar filters
# Dropdowns are blank on first load; a filter applies only after selection.
# ------------------------------------------------------------
st.sidebar.title("Analysis Filters")

def clear_filters():
    for key in (
        "selected_region", "selected_state", "selected_mode", "selected_dates",
        "filter_lead_time", "lead_time_cap",
    ):
        st.session_state.pop(key, None)

st.sidebar.button("Clear filters", on_click=clear_filters, use_container_width=True)

selected_region = st.sidebar.selectbox(
    "Customer region", sorted(df["Region"].dropna().unique()),
    index=None, placeholder="Choose a region", key="selected_region",
)
selected_state = st.sidebar.selectbox(
    "Customer state", sorted(df["State/Province"].dropna().unique()),
    index=None, placeholder="Choose a state", key="selected_state",
)
selected_mode = st.sidebar.selectbox(
    "Shipping mode", sorted(df["Ship Mode"].dropna().unique()),
    index=None, placeholder="Choose a shipping mode", key="selected_mode",
)

filtered_df = df.copy()
if selected_region:
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_state:
    filtered_df = filtered_df[filtered_df["State/Province"] == selected_state]
if selected_mode:
    filtered_df = filtered_df[filtered_df["Ship Mode"] == selected_mode]

valid_dates = df["Order Date"].dropna()
if not valid_dates.empty:
    selected_dates = st.sidebar.date_input(
        "Order date range (optional)", value=None,
        min_value=valid_dates.min().date(), max_value=valid_dates.max().date(),
        key="selected_dates",
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered_df = filtered_df[
            filtered_df["Order Date"].dt.date.between(start_date, end_date)
        ]

filter_lead_time = st.sidebar.checkbox(
    "Filter by recorded lead time", value=False, key="filter_lead_time"
)
if filter_lead_time:
    maximum_lead = int(pd.to_numeric(df["Shipping Lead Time"], errors="coerce").max())
    lead_cap = st.sidebar.slider(
        "Maximum recorded lead time (days)", 0, max(30, maximum_lead),
        min(30, maximum_lead), key="lead_time_cap"
    )
    filtered_df = filtered_df[
        pd.to_numeric(filtered_df["Shipping Lead Time"], errors="coerce") <= lead_cap
    ]

st.sidebar.caption(f"Displaying {len(filtered_df):,} of {len(df):,} records.")


# ------------------------------------------------------------
# 6. Main business KPIs
# ------------------------------------------------------------
st.subheader("Business Overview")

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()
total_lines = len(filtered_df)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Sales", f"${total_sales:,.2f}")
kpi2.metric("Gross Profit", f"${total_profit:,.2f}")
kpi3.metric("Units Sold", f"{total_units:,.0f}")
kpi4.metric("Order Lines", f"{total_lines:,}")
st.caption(f"Unique orders in current selection: {filtered_df['Order ID'].nunique():,}")

st.divider()


# ------------------------------------------------------------
# 7. Factory performance
# ------------------------------------------------------------
st.subheader("Factory Performance")

factory_summary = (
    filtered_df.groupby("Factory", dropna=False)
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
        Order_Lines=("Order ID", "count"),
    )
    .reset_index()
    .sort_values("Sales", ascending=False)
)

st.dataframe(
    factory_summary,
    use_container_width=True,
    hide_index=True,
)

unmapped_products = sorted(
    filtered_df.loc[filtered_df["Factory"].isna(), "Product Name"]
    .dropna()
    .unique()
    .tolist()
)

if unmapped_products:
    st.warning(
        "These products do not have a factory mapping: " + ", ".join(unmapped_products)
    )


# ------------------------------------------------------------
# 8. Regional and state sales charts
# ------------------------------------------------------------
st.subheader("Geographic Sales Performance")

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown("**Sales by Region**")

    region_sales = filtered_df.groupby("Region")["Sales"].sum().sort_values()

    if not region_sales.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        region_sales.plot(kind="barh", ax=ax)
        ax.set_xlabel("Sales")
        ax.set_ylabel("Region")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No regional sales data for these filters.")

with chart_right:
    st.markdown("**Top 10 States by Sales**")

    state_sales = (
        filtered_df.groupby("State/Province")["Sales"].sum().nlargest(10).sort_values()
    )

    if not state_sales.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        state_sales.plot(kind="barh", ax=ax)
        ax.set_xlabel("Sales")
        ax.set_ylabel("State")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No state sales data for these filters.")


# ------------------------------------------------------------
# 9. Product performance
# ------------------------------------------------------------
st.subheader("Top 10 Products by Sales")

product_summary = (
    filtered_df.groupby("Product Name", dropna=False)
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
    )
    .reset_index()
    .sort_values("Sales", ascending=False)
    .head(10)
)

st.dataframe(
    product_summary.style.format(
        {
            "Sales": "${:,.2f}",
            "Gross_Profit": "${:,.2f}",
            "Units": "{:,.0f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# 10. Shipping-mode comparison
# ------------------------------------------------------------
st.subheader("Shipping Mode Usage")

shipping_summary = (
    filtered_df.groupby("Ship Mode", dropna=False)
    .agg(
        Order_Lines=("Order ID", "count"),
        Sales=("Sales", "sum"),
        Units=("Units", "sum"),
    )
    .reset_index()
    .sort_values("Order_Lines", ascending=False)
)

shipping_left, shipping_right = st.columns(2)

with shipping_left:
    st.dataframe(
        shipping_summary.style.format(
            {
                "Sales": "${:,.2f}",
                "Units": "{:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with shipping_right:
    if not shipping_summary.empty:
        st.bar_chart(
            shipping_summary.set_index("Ship Mode")["Order_Lines"],
            horizontal=True,
        )


# ------------------------------------------------------------
# 11. Factory-to-customer route analysis
# ------------------------------------------------------------
st.subheader("Factory-to-Customer Route Analysis")

route_summary = (
    filtered_df.groupby(
        ["Factory", "State/Province"],
        dropna=False,
    )
    .agg(
        Order_Lines=("Order ID", "count"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
    )
    .reset_index()
    .sort_values("Order_Lines", ascending=False)
)

if not route_summary.empty:
    total_route_lines = route_summary["Order_Lines"].sum()

    route_summary["Order_Line_Share_%"] = (
        route_summary["Order_Lines"] / total_route_lines * 100
        if total_route_lines
        else 0
    )

    st.caption("Routes are ranked by order-line volume, not delivery speed.")

    st.dataframe(
        route_summary.head(20).style.format(
            {
                "Sales": "${:,.2f}",
                "Gross_Profit": "${:,.2f}",
                "Units": "{:,.0f}",
                "Order_Line_Share_%": "{:.2f}%",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    top_routes = route_summary.head(10).copy()
    top_routes["Route"] = (
        top_routes["Factory"].fillna("Unknown factory")
        + " → "
        + top_routes["State/Province"].fillna("Unknown state")
    )

    st.markdown("**Top 10 Routes by Order-Line Volume**")
    st.bar_chart(
        top_routes.set_index("Route")["Order_Lines"],
        horizontal=True,
    )
else:
    st.info("No routes match the selected filters.")


# ------------------------------------------------------------
# 12. Factory location map
# ------------------------------------------------------------
st.subheader("Factory Geographic Locations")

st.caption(
    "The map displays the five factory coordinates supplied "
    "in the project specification."
)

st.dataframe(
    factory_locations,
    use_container_width=True,
    hide_index=True,
)

st.map(
    factory_locations.rename(
        columns={
            "Latitude": "latitude",
            "Longitude": "longitude",
        }
    )[["latitude", "longitude"]]
)


# ------------------------------------------------------------
# 13. Customer destination summary
# ------------------------------------------------------------
st.subheader("Top Customer Destinations")

destination_summary = (
    filtered_df.groupby(
        ["City", "State/Province"],
        dropna=False,
    )
    .agg(
        Order_Lines=("Order ID", "count"),
        Sales=("Sales", "sum"),
        Units=("Units", "sum"),
    )
    .reset_index()
    .sort_values("Order_Lines", ascending=False)
)

st.dataframe(
    destination_summary.head(20).style.format(
        {
            "Sales": "${:,.2f}",
            "Units": "{:,.0f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# 14. Data-quality and interpretation notice
# ------------------------------------------------------------
lead_times = pd.to_numeric(filtered_df["Shipping Lead Time"], errors="coerce")
plausible_count = int(lead_times.between(0, 30).sum())
st.warning(
    f"DELIVERY DATE QUALITY: {plausible_count:,} of {len(filtered_df):,} filtered "
    "records have a 0–30 day lead time. The source dates fail validation; treat "
    "delivery-efficiency rankings and delay rates as unverified until corrected."
)

st.info(
    "Factory assignments are based on the product-to-factory mapping "
    "provided in the project specification. Route volumes represent "
    "order lines, not necessarily unique orders or truck journeys."
)

# ------------------------------------------------------------
# 15. Download filtered results
# ------------------------------------------------------------
st.subheader("Export Filtered Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered dataset as CSV",
    data=csv_data,
    file_name="nassau_filtered_analysis.csv",
    mime="text/csv",
)

st.caption("Nassau Candy Distributor | Factory-to-Customer Route Analysis")
