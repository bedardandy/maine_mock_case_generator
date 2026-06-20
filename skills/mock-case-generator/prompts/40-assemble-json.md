# Prompt: Assemble and validate

Assemble everything into ONE JSON object conforming to `catalog/mock_matter.schema.json`.

Checklist before you finish:
- [ ] `schema_version` is `"1.0"`.
- [ ] `provenance` has `mock: true`, `fictional: true`, `generator: "agent-skill"`,
      and `model` set to the model id.
- [ ] `matter` has `matter_id`, `practice_area`, and `jurisdiction`.
- [ ] Party role keys are canonical-compatible; the represented party is duplicated
      under `client`; children are `child_1`, `child_2`, ...
- [ ] All phones are `(207) 555-01xx`; all emails end in `example.com/.org/.net`;
      no real identifiable person is used.
- [ ] `facts` holds the flat, form-specific keys the downstream forms need.
- [ ] Dates are internally consistent across `facts`, `timeline`, and the interview.

Then validate (fix anything reported):
```
python tools/validate.py path/to/matter.json
python tools/project_canonical.py path/to/matter.json    # also validates the canonical projection
```

Both must pass. The projected canonical case is what feeds the downstream
form-filling repos (maine-court-forms, maine-probate-forms, transactional-tax-forms).
