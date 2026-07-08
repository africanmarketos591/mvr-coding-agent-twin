"""Cheap pre-code MVR preflight.

The claim gate sees files. The full committee sees the build plan, but it is a
heavier step. This script is the fast reflex before either: pull category
playbook context, then force the host model to answer three questions before it
writes feature code:

  1. ECLIPSE - who already does this job here?
  2. PERMISSION - what must the market grant, and who grants it?
  3. RAILS - who owns payments, logistics, identity, or distribution?

It authorizes nothing and blocks nothing. It writes a local `PREFLIGHT.md`.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "spine"))


def load_key(keyfile):
    if not keyfile:
        return
    from keyfile_loader import extract_mvr_api_key  # noqa: E402

    with open(keyfile, encoding="utf-8-sig") as handle:
        os.environ["MVR_API_KEY"] = extract_mvr_api_key(handle.read())


def pull_playbook(archetype):
    try:
        import mvr_client as client  # noqa: E402

        _latency, status, data = client.category_playbook(archetype)
        if status == 200 and isinstance(data, dict):
            return data, None
        return {}, f"kernel status {status}"
    except Exception as exc:
        return {}, f"kernel unavailable: {str(exc)[:180]}"


def add_unique(values, new_values):
    seen = set(values)
    for value in new_values:
        if value and value not in seen:
            values.append(value)
            seen.add(value)


def eclipse_queries(idea, country):
    clipped = idea.strip().replace("\n", " ")
    if len(clipped) > 100:
        clipped = clipped[:97] + "..."
    return [
        f'who already provides this in {country}: "{clipped}"',
        f"{country} incumbents startups associations informal alternatives in this exact category",
        f"{country} SACCO chama association offline workflow already used for this job",
        'is the only advantage "an AI can generate this"? if yes, it is pre-eclipsed',
    ]


def write_preflight(path, idea, archetypes, country, playbooks, errors):
    guardians = []
    failures = []
    board_questions = []
    evidence_lanes = []
    for playbook in playbooks:
        add_unique(guardians, [
            item.get("guardian_tier") or item.get("tier") or item.get("name")
            for item in playbook.get("minimum_guardian_map") or []
            if isinstance(item, dict)
        ])
        add_unique(failures, [str(item) for item in playbook.get("failure_modes") or []])
        add_unique(board_questions, [str(item) for item in playbook.get("board_questions") or []])
        add_unique(evidence_lanes, [
            lane.get("stakeholder_class") or lane.get("lane") or lane.get("name")
            for lane in playbook.get("required_local_evidence") or []
            if isinstance(lane, dict)
        ])

    if not guardians:
        guardians = ["macro_regulator", "meso_community", "micro_street"]
    if not board_questions:
        board_questions = [
            "Who already does this job locally?",
            "Who can block adoption even if the product works?",
            "Which evidence gap must close before claims are made?",
        ]
    if not evidence_lanes:
        evidence_lanes = guardians

    status = "LIVE" if playbooks and not errors else "DEGRADED"
    error_line = "; ".join(errors) if errors else "none"
    query_lines = "\n".join(f"- {query}" for query in eclipse_queries(idea, country))
    gate_lines = "\n".join(
        f"- {lane}: who grants permission, which licence or channel rule applies, and what evidence proves it?"
        for lane in evidence_lanes
    )
    board_lines = "\n".join(f"- {question}" for question in board_questions[:6])
    failure_line = ", ".join(failures[:6]) if failures else "unknown until research"

    text = f"""# PREFLIGHT - answer before writing feature code

This is the cheap MVR reflex. It does not authorize claims. It prevents the model from
building first and discovering the market later.

**Idea:** {idea}
**Archetype(s):** {', '.join(archetypes)}
**Country / market:** {country}
**Kernel playbook status:** {status}
**Kernel notes:** {error_line}

## Stop: the three questions that kill most builds

1. **ECLIPSE:** who already does this job here, formally or informally?
   - Verdict before code: `UNKNOWN | survives | pre-eclipsed`
2. **PERMISSION:** what must the market grant, and who grants it?
   - Verdict before code: `UNKNOWN | permission path named | blocked`
3. **RAILS:** who owns payments, logistics, identity, distribution, or trust rails?
   - Verdict before code: `UNKNOWN | ride rails | fight rails`

## Guardian veto surface

Guardian tiers: {', '.join(guardians)}

Failure modes to check: {failure_line}

Board questions:
{board_lines}

## Eclipse scan to run now

{query_lines}

If the only advantage is "AI can generate this", stop. Every buyer owns a frontier
model. The build survives only if it has evidence, permission, distribution, or a
relationship the model cannot hallucinate into being.

## Public research pack

If any named public fact will enter the charter, run:

```bash
python scripts/twin_public_research.py --init --idea "{idea}" --country "{country}" --archetype {archetypes[0]}
```

Use browser/search tools to fill `mvr/public_research/source_ledger.json`, then
validate it with:

```bash
python scripts/twin_public_research.py --validate
```

No source/date/status, no user-facing public fact.

## Permission gates to name

{gate_lines}

## The 0.30 reflex

Founder claims about traction, relationships, permission, or market demand stay at
0.30 weight until corroborated or attested. Persuasive wording is not evidence.

## Do not proceed to feature code until

- [ ] Eclipse verdict is written with named incumbents or informal alternatives.
- [ ] Permission gates are named with licence/channel/guardian owner.
- [ ] Rails are classified as ride or fight, with the rail owner named.
- [ ] Any remaining UNKNOWN is escalated to `scripts/twin_committee.py`.
"""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main():
    parser = argparse.ArgumentParser(description="Write a cheap pre-code MVR preflight card.")
    parser.add_argument("--idea", required=True)
    parser.add_argument("--archetype", action="append", required=True, default=[])
    parser.add_argument("--country", required=True)
    parser.add_argument("--keyfile")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--out", default="PREFLIGHT.md")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    os.makedirs(root, exist_ok=True)
    os.environ["CLAUDE_PROJECT_DIR"] = root
    load_key(args.keyfile)

    playbooks = []
    errors = []
    for archetype in args.archetype:
        playbook, error = pull_playbook(archetype)
        if playbook:
            playbooks.append(playbook)
        if error:
            errors.append(f"{archetype}: {error}")

    out = args.out if os.path.isabs(args.out) else os.path.join(root, args.out)
    write_preflight(out, args.idea, args.archetype, args.country, playbooks, errors)
    print(f"PREFLIGHT written -> {out}")
    print("Answer ECLIPSE + PERMISSION + RAILS before writing feature code.")


if __name__ == "__main__":
    main()
