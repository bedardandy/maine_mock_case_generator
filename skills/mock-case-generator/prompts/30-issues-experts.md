# Prompt: Spot issues and add experts

## Issues
Spot the legal `issues` a competent attorney would identify. For each:
- `issue`: the question presented.
- `category`: short label.
- `governing_law`: a realistic statute/rule citation (e.g. `19-A M.R.S. § 1653`,
  `18-C M.R.S. § 3-301`, `IRC § 2056`). Illustrative, not authoritative.
- `sub_questions`: 1–3 concrete questions the issue breaks into.
- `client_position` (optional): what the client contends.
- `strength`: strong | moderate | weak | unknown.

Aim for 3–6 issues that match the practice area.

## Expert opinions
Add `expert_opinions` only where a real matter would retain an expert (custody
evaluation, business/real-estate valuation, forensic accounting, DV dynamics, etc.).
For each:
- `expert`: `{name (invented), field, credentials, retained_by (canonical role)}`
- `topic`, `opinion` (1–2 sentences), `basis` (methodology/materials).

Transactional matters may have zero or one expert; estate-tax and contested
family/probate matters usually have one to three.
