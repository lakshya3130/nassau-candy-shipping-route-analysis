"""Reproducible analysis for the Nassau Candy shipping project.

Run from any directory with: python analysis.py
Shipment-date metrics are audited but deliberately excluded from rankings when
the supplied dates fail basic plausibility checks.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "Nassau Candy Distributor.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack", "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack", "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory", "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory", "Kazookles": "The Other Factory",
}

def main():
    df = pd.read_csv(DATA, dtype={"Postal Code": "string"})
    for col in ("Order Date", "Ship Date"):
        df[col] = pd.to_datetime(df[col], format="%d-%m-%Y", errors="coerce")
    for col in ("Sales", "Gross Profit", "Units", "Cost"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY)
    df["Shipping Lead Time"] = (df["Ship Date"] - df["Order Date"]).dt.days
    lead = df["Shipping Lead Time"]
    valid_dates = df["Order Date"].notna() & df["Ship Date"].notna()
    plausible = valid_dates & lead.between(0, 30)

    # The source contains 10,194 of 10,194 durations above 30 days. Keep the
    # raw values for auditability and do not silently repair or infer dates.
    df.to_csv(OUT / "cleaned_shipments.csv", index=False)
    audit = pd.DataFrame([
        ("Total records", len(df)),
        ("Duplicate rows", int(df.duplicated().sum())),
        ("Missing order dates", int(df["Order Date"].isna().sum())),
        ("Missing ship dates", int(df["Ship Date"].isna().sum())),
        ("Order date range", f"{df['Order Date'].min().date()} to {df['Order Date'].max().date()}"),
        ("Ship date range", f"{df['Ship Date'].min().date()} to {df['Ship Date'].max().date()}"),
        ("Ship dates before order dates", int((lead < 0).sum())),
        ("Lead times over 30 days", int((lead > 30).sum())),
        ("Records with plausible 0-30 day lead time", int(plausible.sum())),
        ("Unmapped products", int(df["Factory"].isna().sum())),
    ], columns=["Check", "Result"])
    audit.to_csv(OUT / "date_audit_summary.csv", index=False)

    # Descriptive commercial/geographic metrics are supported by the source.
    def aggregate(keys, path):
        result = df.groupby(keys, dropna=False).agg(
            Total_Sales=("Sales", "sum"), Total_Profit=("Gross Profit", "sum"),
            Total_Units=("Units", "sum"), Order_Lines=("Order ID", "size"),
            Unique_Orders=("Order ID", "nunique"),
        ).reset_index().sort_values("Total_Sales", ascending=False)
        result.to_csv(OUT / path, index=False)
        return result
    region = aggregate(["Region"], "region_performance.csv")
    state = aggregate(["State/Province"], "state_performance.csv")
    products = aggregate(["Product Name"], "product_performance.csv")
    modes = aggregate(["Ship Mode"], "shipping_mode_summary.csv")
    factory_region = aggregate(["Factory", "Region"], "factory_region_summary.csv")
    routes = df.groupby(["Factory", "State/Province"], dropna=False).agg(
        Order_Lines=("Order ID", "size"), Unique_Orders=("Order ID", "nunique"),
        Sales=("Sales", "sum"), Gross_Profit=("Gross Profit", "sum"), Units=("Units", "sum"),
    ).reset_index().sort_values("Order_Lines", ascending=False)
    routes.to_csv(OUT / "route_summary.csv", index=False)

    summary = [
        "NASSAU CANDY DISTRIBUTOR — PROJECT FINDINGS", "",
        f"Records: {len(df):,}; unique orders: {df['Order ID'].nunique():,}",
        f"Sales: ${df['Sales'].sum():,.2f}; gross profit: ${df['Gross Profit'].sum():,.2f}; units: {df['Units'].sum():,.0f}",
        f"Leading region by sales: {region.iloc[0]['Region']} (${region.iloc[0]['Total_Sales']:,.2f})",
        f"Leading state by sales: {state.iloc[0]['State/Province']} (${state.iloc[0]['Total_Sales']:,.2f})",
        f"Leading product by sales: {products.iloc[0]['Product Name']} (${products.iloc[0]['Total_Sales']:,.2f})",
        f"Most-used mode by order lines: {modes.sort_values('Order_Lines', ascending=False).iloc[0]['Ship Mode']}",
        "", "DATE QUALITY: Not fit for delivery-efficiency measurement.",
        f"Order dates: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}; ship dates: {df['Ship Date'].min().date()} to {df['Ship Date'].max().date()}.",
        f"{int((lead > 30).sum()):,}/{len(df):,} records have computed lead times over 30 days; {int(plausible.sum()):,} have 0–30 day lead times.",
        "Do not publish route speed, delay rate, or efficiency score rankings until corrected shipment dates are supplied.",
        "Factory-to-state route tables therefore report shipment/order volume and commercial totals only.",
    ]
    (OUT / "project_summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("Wrote reproducible outputs to", OUT)

if __name__ == "__main__":
    main()
