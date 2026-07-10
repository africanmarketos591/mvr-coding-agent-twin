# c04 — Offline-First Duka Bookkeeping (Kenya)

## v1 (the fast, honest starting point)
A phone app a shopkeeper opens to record a sale in 2 taps, track stock, and get a low-stock nudge. It explicitly does NOT touch money — that constraint is a feature: no licensing burden, faster to ship, easier to trust. v1 = record sales, manage stock, see today's numbers.

## Core features
- Quick sale entry (item, qty, price) — must work in seconds at the counter.
- Product/inventory list with current stock counts.
- Automatic stock decrement on sale; low-stock flag with a threshold per item.
- Daily/weekly sales summary (revenue, top items). Fully usable offline.

## Tech approach
- Offline-first mobile app: Flutter or React Native with a local DB (SQLite/WatermelonDB) as the source of truth.
- Background sync to a backend (Postgres) when connectivity returns; conflict resolution kept simple (last-write-wins per record, since it's single-user per shop).
- Android-first (that's the market). Keep the APK light; assume low-end devices and patchy data.

## Go-to-market
- Free to start — remove all friction to habit formation. Land shops one market/street at a time via field reps who onboard and seed the first product list.
- Grow through word of mouth between neighboring dukas; add a light referral.
- Monetize later with a low monthly fee once bookkeeping is a daily habit, plus optional paid add-ons (reports, multi-shop). Stay away from money-holding to keep the value prop and the regulatory profile clean.

## Biggest risk
Daily-use retention. Manual entry is a chore. Make entry faster than a paper book or it won't stick.
