# c11 — Drone Delivery of Blood & Medicines (Rural Rwanda)

## v1 (reality check: this is aerospace + logistics, not an app)
Be straight with the founder: the "product" here is a regulated, safety-critical aviation operation. Software is a small part. Zipline already operates nationally in Rwanda, so the honest v1 is either (a) a genuinely differentiated operational model, or (b) the logistics/dispatch software layer that clinics and hospitals use — which is where a fast software builder can actually add value quickly. I'd scope v1 as the ordering + dispatch + tracking system, partnering for the flight hardware.

## Core features
- Clinic ordering app/USSD: request blood/medicine, specify urgency, confirm receipt.
- Dispatch console: hospital-side view of orders, stock, and fulfillment status.
- Delivery tracking + confirmation; cold-chain/inventory records for auditability.
- Works on low-bandwidth (SMS/USSD fallback) — rural clinics can't assume connectivity.

## Tech approach
- Web console for hospital hubs; simple mobile/USSD interface for clinics.
- Node/Postgres backend; integrate with the drone operator's flight/telemetry systems via API rather than building aircraft.
- Offline-tolerant, audit-logged (medical + regulatory requirements).

## Go-to-market
- This is sold to Ministry of Health / hospital networks, not individuals — long procurement, high trust bar. Partner with existing drone operators and regulators (RCAA) from day one.
- Prove value at a handful of clinics with measurable outcomes (delivery time, stockout reduction).

## Biggest risk
Regulation, safety, and capital. The flight side is not a fast-build. Position as the software/dispatch layer and partner for aviation, or the timeline and cost are misjudged. Set expectations honestly.
