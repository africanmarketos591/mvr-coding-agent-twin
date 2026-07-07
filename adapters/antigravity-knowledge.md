# Antigravity adapter — MVR Twin (add as a Knowledge item; wire hooks + scheduled tasks)

Binding: load `mvr-coding-agent-twin/CLAUDE.md` as project doctrine. Antigravity 2.0 hosts get
the FULL Twin experience — map these host features:

- **Hooks:** wire the claim gate (`hooks/claim_gate.py`) to write-tool lifecycle events; wire
  the heartbeat (`hooks/heartbeat.py`) to prompt-submission events; formats differ from
  Claude Code's `settings-hooks.json` — same stdin/stdout contracts, adapt the wrapper only.
- **Scheduled tasks:** run `scripts/settle.py` quarterly (the settlement pulse) and after any
  charter checkpoint date passes. Settlement facts never come from user confession.
- **Browser subagent:** use it for (a) evidence-grade research — verify incumbents' actual
  product surfaces, screenshot into the charter's source ledger with URL+date; (b) executing
  the settlement pulse checklist (registry, domain, listing, dormancy) end-to-end.
- **Artifacts:** emit the Build Charter and MIRROR as Artifacts; attach browser recordings and
  screenshots as source-ledger evidence.
- **Knowledge base:** store settled-outcome digests as knowledge items so calibration context
  survives across sessions (never store raw personal passport data as shared knowledge).

Also install the git pre-commit gate as defense-in-depth:
`echo 'python mvr-coding-agent-twin/hooks/pre_commit_claim_gate.py || exit 1' >> .git/hooks/pre-commit`
