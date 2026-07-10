# c08 — B2B FMCG Ordering + Delivery (Lagos)

## v1 (ordering + delivery first; credit is phase 2)
Let shop owners order FMCG stock from suppliers and get it delivered. Ship the ordering-and-fulfillment loop before touching credit — credit is a lending business with its own risk, capital, and regulatory weight, and it's worthless if the core commerce doesn't work. v1 = catalog, order, deliver, pay on delivery.

## Core features
- Shop-owner app: browse supplier catalog with prices, cart, place order, reorder favorites.
- Order management + delivery scheduling; status tracking.
- Payments: cash/transfer on delivery first, plus in-app options (Paystack/Flutterwave).
- Ops/admin: inventory, order routing, simple delivery dispatch.

## Tech approach
- Android-first mobile app (React Native/Flutter) for shop owners; internal web dashboard for ops.
- Node/Postgres backend; start with a curated catalog from a few key suppliers/distributors rather than an open marketplace.
- Own or partner the last-mile delivery early so reliability is controllable.

## Go-to-market
- Density play: one or two Lagos markets/neighborhoods, deep supplier coverage so shops can actually fill a full basket.
- Field reps onboard shops and take first orders in person; WhatsApp/agent support.
- Compete on price transparency and reliable next-day delivery vs. the informal distributor status quo.

## Phase 2: credit
Only after you have order history. Use that transaction data to underwrite small BNPL-style stock credit — carefully, with real capital and default modeling. Don't front-load lending risk before the commerce engine is proven.
