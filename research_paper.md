# Factory-to-Customer Shipping Route Analysis for Nassau Candy Distributor

## Executive abstract

This project assesses whether the supplied order and shipment records can support route-level delivery-efficiency decisions and reports the commercial and geographic patterns that are supportable. The source contains 10,194 line records and 8,549 distinct order IDs. It reports $141,783.63 in sales, $93,442.80 in gross profit, and 38,654 units. Product-to-factory assignments use the project specification. The shipment dates fail a basic plausibility check: order dates run from January 2, 2024 through December 31, 2025, while ship dates run from June 30, 2026 through June 28, 2030; every computed duration exceeds 30 days. As a result, this report does not claim route speed, delay rate, or delivery efficiency. It provides auditable route volume and recommends obtaining corrected shipment dates before making transportation decisions.

## 1. Business question

Nassau Candy Distributor needs to understand how factory-to-customer routes perform, where shipment volume is concentrated, and how ship mode and geography relate to delivery times. The requested route definition is factory to customer state or region, with route volume, average lead time, variability, delay frequency, and a normalized efficiency score.

## 2. Data and method

The analysis uses the provided 10,194-row CSV. Dates are parsed using the source's stated day-month-year format. Product names map to factories using the supplied mapping table. Sales, gross profit, units, and costs are converted to numeric values. Routes are grouped by mapped factory and destination state; summaries include order-line volume and unique order counts to keep those units distinct.

The proposed lead-time measure is `Ship Date − Order Date`. Since the source documentation does not define a delay threshold, 30 days is used only as a diagnostic plausibility ceiling, not as a business SLA. A record is considered plausible for a future analysis only if both dates parse and the duration is between 0 and 30 days inclusive. The supplied data has no qualifying records. No date offsets or imputed values are applied.

## 3. Findings supported by the data

- Sales total **$141,783.63**, gross profit totals **$93,442.80**, and units total **38,654**.
- **Pacific** is the largest region by sales at **$46,301.53**; **California** is the leading state at **$27,917.40**.
- **Wonka Bar - Triple Dazzle Caramel** is the top product by sales. **Standard Class** is the most used ship mode by order-line count (6,120 lines).
- Route summaries can identify where order lines, unique orders, sales, and units are concentrated. They cannot establish which routes are fast or reliable with the current dates.

## 4. Data-quality assessment and limitations

All 10,194 rows have computed durations greater than 30 days, and the earliest ship date is later than the latest order date. This is strong evidence that the date fields are not suitable for delivery-performance measurement as supplied. The date issue is not repaired by this analysis because no authoritative corrected dates or transformation rule are available. Treating the 100% over-30-day share as a real delay rate would confuse a source-data defect with operational performance.

The source is line-item data. Row counts are therefore called order lines, while distinct `Order ID` counts are reported separately; neither should be called truck journeys. The mapping assigns each product to one factory, as specified, and does not prove actual fulfillment origin. Sales and profit are descriptive and do not represent freight cost. The supplied factory coordinates support showing factory locations, but customer coordinates are absent, so a true shipment route map cannot be drawn from this dataset alone.

## 5. Recommendations

1. Obtain the corrected source extract or a documented date correction from the data owner. Preserve original values and record any correction rule and audit trail.
2. Validate dates before reporting: parsed dates, ship date not before order date, duration distribution, and counts beyond the agreed SLA. Confirm the expected business range with operations.
3. Confirm whether one row is an order line and whether one order can be split across shipments. Add shipment/tracking identifiers and actual origin when possible.
4. Once dates pass validation, calculate route median and mean lead time, standard deviation or interquartile range, shipment count, and delay share against an approved SLA. Compare ship modes only after controlling for destination and service mix.
5. Add freight charges and customer geocodes if management needs cost-time tradeoffs and a customer-level map.

## 6. Reproducibility and deliverables

Run `python analysis.py` from the project folder to regenerate CSV summaries and the date audit in `outputs/`. The Streamlit application is launched with `streamlit run dashboard.py`. The dashboard presents commercial/geographic metrics and explicitly flags that delivery efficiency cannot be validated with the present dates.

## Conclusion

The dataset supports useful sales, product, mode-usage, and route-volume analysis. It does not support the core delivery-efficiency rankings yet. Corrected shipment dates are the necessary next input for a reliable assessment of fast routes, bottlenecks, and delay frequency.
