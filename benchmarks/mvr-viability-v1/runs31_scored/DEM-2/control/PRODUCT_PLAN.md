# c07 — Student Social Network (Nairobi Universities)

## v1 (start narrow: one campus, one killer use)
Social networks die from empty rooms. Don't launch a general "student network" across all universities — launch on ONE campus around the single most-wanted thing. Notes-sharing + events is a strong wedge because it has utility even before the social graph fills in. v1 = one university, course-based note sharing + an events feed.

## Core features
- Sign up with student email (verifies real students, seeds trust).
- Course/unit groups: upload and find notes/past papers.
- Campus events feed: post, RSVP, discover.
- Lightweight profiles + follow; keep social features minimal until density exists.

## Tech approach
- Mobile-first: React Native app + a mobile web fallback for shareable links (events, notes drive virality via WhatsApp).
- Backend Node/Postgres; file storage (S3) for notes; push notifications for events/replies.
- Ship fast and cheap — this is about distribution, not tech.

## Go-to-market
- The 500-person waitlist is a real asset but not proof of retention — treat it as a launch cohort, not a victory. Convert them first and measure weekly active use.
- Concentrate everything on one campus to reach the density where the feed feels alive. Use campus ambassadors, seed events and notes manually, integrate with WhatsApp groups rather than fighting them.
- Only expand to a second campus once the first shows real weekly retention.

## Biggest risk
Retention past novelty and the empty-network problem. Density on one campus beats thin presence everywhere. Utility (notes/events) must carry it until the social graph is dense enough to be the draw.
