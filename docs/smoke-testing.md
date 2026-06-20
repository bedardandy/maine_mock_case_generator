# Smoke testing a legal workflow pipeline

The point of this repo: generate fictional matters that drive your pipeline end-to-end,
so you can confirm the wiring works before pointing it at real data.

## The built-in smoke harness

`tools/smoke.py` exercises the generator's own contract: for every scenario and a range
of seeds it generates → validates → checks for placeholder leaks → projects → validates
the canonical projection. It exits non-zero on any failure, so it gates CI.

```bash
python tools/smoke.py                 # all scenarios, 3 seeds each
python tools/smoke.py --count 10      # more volume
python tools/smoke.py --scenarios estate-tax-706,decedent-estate-informal -v
```

Output:

```
scenario                         runs  matter  clean  canon  status
------------------------------------------------------------------------
business-formation-scorp            3       3      3      3  PASS
...
7 scenarios, 21 runs, 0 failure(s).
```

Columns: `matter` (valid against the Mock Matter schema), `clean` (no unresolved
`{template}` placeholders leaked), `canon` (the projection validates against the
downstream contract).

## Extending the smoke test through the *whole* pipeline

The built-in harness stops at the canonical contract. To smoke-test all the way to
filled forms, add a step that feeds the projection into a downstream filler:

```bash
for s in $(python tools/generate.py --list | tail -n +2); do
  python tools/generate.py "$s" --seed 0 --canonical > /tmp/case.json
  # hand /tmp/case.json to the matching downstream repo's fill engine and assert it
  # produces a draft without errors
done
```

## Using it in CI

A minimal GitHub Actions job:

```yaml
name: smoke
on: [push, pull_request]
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: python -m pytest -q
      - run: python tools/smoke.py --count 5
```

## Volume / fuzz testing

Because deterministic generation is seedable, you can sweep a wide seed range to shake
out edge cases (unusual child counts, boolean facts, large dollar amounts):

```bash
python tools/smoke.py --count 100        # 100 seeds per scenario
```

Every seed is reproducible: if seed 73 of `minor-guardianship` ever breaks a downstream
form, `python tools/generate.py minor-guardianship --seed 73` reproduces the exact input.
