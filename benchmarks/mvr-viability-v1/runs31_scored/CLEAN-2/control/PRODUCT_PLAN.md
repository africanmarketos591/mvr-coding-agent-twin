# c05 — QR Digital Menu + Kitchen Orders (Nairobi)

## v1 (dine-in ordering, no money handling)
A restaurant gets a QR code per table. Diner scans, browses the menu on their phone, places an order, and it prints in the kitchen. Payment stays at the existing till — the app never touches money, which keeps us out of PSP licensing and speeds up shipping. v1 = menu builder + QR + order-to-kitchen.

## Core features
- Restaurant dashboard: build menu (categories, items, prices, photos, availability toggle).
- Per-table QR generation.
- Diner web page (no app install): browse, add to cart, submit order with table number.
- Kitchen ticket: live order screen (KDS) plus optional receipt printer output.
- Order status + basic daily order log for the manager.

## Tech approach
- Mobile web for diners (no install) — Next.js/React, works on any phone camera.
- Backend Node/Postgres; real-time order push to kitchen via WebSockets.
- Printing via a cloud-printable format (ESC/POS to a network/thermal printer) or a tablet-based kitchen display to avoid hardware dependency at launch.

## Go-to-market
- Target mid-size Nairobi restaurants and cafes with table service and menu churn.
- Free QR menu as the wedge (kills print costs, easy yes), then upsell ordering + KDS on a monthly SaaS fee per location.
- Direct sales on the ground; a visible "scan to order" table tent doubles as marketing to other restaurateurs who dine there.

## Biggest risk
Kitchen workflow adoption. If staff don't trust the tickets, they revert to shouting orders. Nail printer/KDS reliability and train the first few sites hands-on.
