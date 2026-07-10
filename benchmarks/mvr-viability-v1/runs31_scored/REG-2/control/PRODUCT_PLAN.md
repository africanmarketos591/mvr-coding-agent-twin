# c10 — Earned-Wage Access for Factory Workers (Lagos)

## v1 (employer-integrated, not consumer lending)
Workers draw an advance on wages already earned and repay automatically on payday. The right shape is B2B2C: sign the employer first. That gives you verified earned-wage data and payroll-deduction repayment, which turns this from risky lending into low-risk access. v1 = one factory, integrated with their payroll.

## Core features
- Employer onboarding + payroll/attendance integration to compute accrued earned wages.
- Worker app: see available balance, request an advance (capped at a % of earned wages), receive funds instantly.
- Automatic repayment via payroll deduction on payday.
- Transparent flat fee (not interest); clear limits to prevent over-draw.

## Tech approach
- Worker app: Android-first, lightweight, Mobile Money + bank payout (Paystack/Flutterwave, NIBSS).
- Backend Node/Postgres; secure integration with employer payroll/HR systems (or a simple CSV/attendance import for the first sites).
- Ledger discipline from day one — every advance, fee, and repayment reconciled.

## Go-to-market
- Sell to factory HR/finance as a free retention + wellbeing benefit; the employer is the channel to hundreds of workers at once.
- Land 1-2 factories, onboard whole shifts, prove repayment works via deduction before scaling.
- Fund advances from a modest working-capital facility; keep advance caps conservative early.

## Biggest risk
Repayment integrity and regulatory framing (CBN/lending rules). Payroll-deduction repayment and the employer relationship are what de-risk it — don't launch consumer-direct without them.
