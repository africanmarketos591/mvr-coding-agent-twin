# c12 — Diaspora Investment Pool (Kenya)

## v1 (regulation first — this is a licensed activity, not just an app)
Critical caveat for the founder: pooling members' money and investing it in stocks and money-market funds is a regulated collective investment scheme. In Kenya that means the CMA (Capital Markets Authority), and cross-border diaspora flows add more. You cannot ship this like a normal app — the "v1" gate is legal structure, not code. Build the software against a compliant structure (e.g. partnering with a licensed fund manager) rather than custodying and investing money yourself.

## Core features (once the structure is in place)
- Onboarding with KYC/AML (diaspora + local), tiered verification.
- Recurring contributions via Mobile Money (M-Pesa) and card/bank for diaspora.
- Allocation into a licensed money-market fund / equities product held by the regulated partner.
- Dashboard: balance, contributions, returns; withdrawals with clear timelines.

## Tech approach
- Mobile app (React Native) + web; Node/Postgres.
- Integrate a licensed fund manager / custodian's APIs for the actual investing — do NOT hold or invest client funds directly.
- Bank-grade security, full ledger + audit trail, KYC/AML provider integration.

## Go-to-market
- Trust is the entire product for a money app. Lead with the licensed partner's credibility and transparent reporting.
- Target Kenyan diaspora communities (US/UK/Gulf) via community groups and referrals; local members via M-Pesa ease.

## Biggest risk
Regulatory and trust failure. Handle licensing (CMA), KYC/AML, and custody through licensed partners BEFORE writing consumer features. Get this wrong and it's not a bug — it's a shutdown.
