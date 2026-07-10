# c02 — Boda-Boda Super-App (Kampala)

## v1 (ship the ride-hail loop first)
Resist "super-app." Build one thing that works: hail a boda, driver accepts, ride happens, pay. Parcels come after ride-hailing has liquidity. A super-app with no riders and no drivers is just an expensive icon grid.

## Core features
- Rider app: set pickup/drop, see nearby drivers, request, live track, fare estimate.
- Driver app: go online, receive/accept requests, navigate, mark complete.
- Payments: cash first (dominant reality), plus in-app Mobile Money (MTN MoMo, Airtel Money) as the push toward cashless.
- Ratings both ways; basic trip history.

## Tech approach
- React Native for both apps (shared codebase), or Flutter. Node/Postgres backend + Redis for live driver locations and dispatch matching.
- Google Maps / Mapbox for routing; simple nearest-driver dispatch to start.
- Mobile Money via MTN/Airtel APIs or an aggregator (e.g. Flutterwave) — keep money flows auditable from day one.

## Go-to-market
- Solve the chicken-and-egg by hand: recruit 100-200 drivers in a few dense stages/neighborhoods, guarantee minimum earnings for the first weeks so they stay online.
- Launch in ONE catchment (e.g. Makerere/Kampala CBD) to keep ETAs short. Density beats coverage.
- Rider acquisition via referral credits and stage-level street activation. Compete with SafeBoda on driver treatment and reliability, not just price.

## Biggest risk
Two-sided liquidity and driver loyalty. Incumbents exist. Win a small area completely before spreading, and add parcels only once drivers have idle capacity.
