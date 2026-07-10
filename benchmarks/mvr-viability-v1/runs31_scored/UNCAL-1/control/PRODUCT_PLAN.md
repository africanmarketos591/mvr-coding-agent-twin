# c03 — Trucking Compliance SaaS (Germany)

## v1 (ship a focused compliance tool, not a TMS)
German long-haul is heavily regulated. v1 should ingest tachograph data and answer one urgent question for a fleet manager: "Which drivers are about to breach, and am I audit-ready?" Don't try to be a full fleet-management suite yet.

## Core features
- Upload/import digital tachograph (.DDD) and driver-card files; parse activities.
- Driving/rest-time analysis against EU 561/2006 + Mobility Package rules; flag violations and near-breaches.
- Missing-download alerts (legal deadlines for card/mass-memory downloads).
- Driver + vehicle roster, per-driver status dashboard, exportable audit reports (PDF) for BAG inspections.

## Tech approach
- Web app: TypeScript/React front end, Node or Java/Kotlin backend, Postgres.
- Core is a well-tested tachograph parser and a rules engine encoding 561/2006 and Mobility Package (weekly rest, return-home, posting rules). This is the moat — invest here.
- Role-based access; GDPR-compliant hosting in the EU (driver data is sensitive personal data).

## Go-to-market
- Sell to fleet managers of small-to-mid fleets (20-100 trucks) who feel audit pain but can't afford heavyweight incumbents (Webfleet, VDO TIS-Web).
- Lead-gen through Spedition trade associations, LinkedIn, and a free "compliance check" of an uploaded tachograph file.
- Land-and-expand: start with compliance reporting, then add planning/telematics.

## Biggest risk
Regulatory correctness. A wrong "you're compliant" is a liability. Validate the rules engine with a compliance/legal advisor before selling, and keep it updated as Mobility Package phases in.
