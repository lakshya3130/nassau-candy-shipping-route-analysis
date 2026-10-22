"""Generate static, source-supported project charts from analysis outputs."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"

def save_bar(series, title, xlabel, filename, horizontal=True):
    if series.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    (series.sort_values().plot.barh(ax=ax) if horizontal else series.plot.bar(ax=ax))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=160)
    plt.close(fig)

def main():
    region = pd.read_csv(OUT / "region_performance.csv")
    state = pd.read_csv(OUT / "state_performance.csv")
    products = pd.read_csv(OUT / "product_performance.csv")
    modes = pd.read_csv(OUT / "shipping_mode_summary.csv")
    routes = pd.read_csv(OUT / "route_summary.csv")
    save_bar(region.set_index("Region")["Total_Sales"], "Sales by Region", "Sales ($)", "sales_by_region.png")
    save_bar(state.nlargest(10, "Total_Sales").set_index("State/Province")["Total_Sales"], "Top 10 States by Sales", "Sales ($)", "top_10_states_by_sales.png")
    save_bar(products.nlargest(10, "Total_Sales").set_index("Product Name")["Total_Sales"], "Top 10 Products by Sales", "Sales ($)", "top_10_products_by_sales.png")
    save_bar(modes.set_index("Ship Mode")["Order_Lines"], "Order Lines by Shipping Mode", "Order lines", "shipping_mode_distribution.png")
    route_names = routes.assign(Route=routes["Factory"].fillna("Unknown") + " → " + routes["State/Province"].fillna("Unknown"))
    save_bar(route_names.head(10).set_index("Route")["Order_Lines"], "Top 10 Factory-to-State Routes by Order-Line Volume", "Order lines", "top_10_routes_by_volume.png")
    print(f"Charts saved to {OUT}")

if __name__ == "__main__":
    main()
