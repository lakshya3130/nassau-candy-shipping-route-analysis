# Executive Summary

## Factory-to-Customer Shipping Route Analysis

**Nassau Candy Distributor | Decision brief**

### What the data shows

The supplied file contains 10,194 order-line records across 8,549 distinct orders. It records **$141,783.63 in sales**, **$93,442.80 in gross profit**, and **38,654 units**. Pacific leads regional sales ($46,301.53), California leads state sales ($27,917.40), and Standard Class is the most frequently used shipping mode (6,120 order lines). Product-to-factory assignments follow the project mapping.

### What the data cannot show yet

Delivery efficiency, route delay frequency, and ship-mode speed cannot be assessed reliably. Order dates span January 2024–December 2025, but recorded ship dates span June 2026–June 2030; all 10,194 computed lead times exceed 30 days. These records should not be interpreted as proof of extremely late deliveries. The date fields require correction or authoritative explanation.

### Recommended actions

1. Request a corrected shipment extract or a documented correction rule from the data owner.
2. Approve a service-level threshold and validate date ranges, negative durations, and outliers before publishing delivery KPIs.
3. Confirm fulfillment-origin and shipment identifiers so route counts represent actual shipments rather than item rows.
4. After validation, compare routes using shipment count, median/mean lead time, variability, and SLA delay share. Compare ship modes within comparable destination and service groups.

### Decision

Use the current dashboard for sales, product, geography, ship-mode usage, and route-volume exploration. Defer operational conclusions about fastest routes, bottlenecks, or delivery reliability until shipment-date quality is resolved. The analysis script and audit outputs preserve the evidence and can be rerun when corrected data arrives.
