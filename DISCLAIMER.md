# Disclaimer

**Everything this repository produces is fictional mock data.**

This project generates synthetic legal-matter information for the sole purpose of
**smoke-testing software pipelines**. It is not legal advice, not a real case, and
not connected to any real person, family, estate, business, or dispute.

## What the data is — and is not

- **Fictional.** Names, parties, addresses, dates, dollar amounts, issues, and
  expert opinions are invented by a generator from scenario templates. Every
  generated matter carries `provenance.mock = true` and `provenance.fictional = true`.
- **Not real PII.** The generator deliberately uses values reserved for fiction:
  phone numbers in the `555-01xx` range, `example.com` / `example.org` / `example.net`
  email domains, and made-up street addresses. Real Maine county and court-location
  names are used only so downstream *routing* behaves realistically; they do not
  identify any real person.
- **Not legal advice.** Statutory citations are included to make scenarios realistic
  for testing issue-spotting and form-routing logic. They are illustrative and may be
  inexact, abbreviated, or out of date. Do not rely on them.
- **Not a substitute for real intake.** The simulated interviews, objectives, and
  fact patterns are scaffolding for testing software, not a model of how to interview
  a real client.

## Responsible use

- Do **not** file generated documents with any court or agency.
- Do **not** mix generated mock matters into a production datastore that also holds
  real client data without a clear `mock`/`fictional` partition.
- If you adapt this generator to a new jurisdiction or practice area, keep the
  fictional-data guarantees (reserved phone/email ranges, invented identities) intact.

The downstream form-filling repositories this feeds
(`maine-court-forms`, `maine-probate-forms`, `transactional-tax-forms`) carry their own
disclaimers: all of their output is **draft material requiring attorney review**. The
same applies here, doubly so, because the inputs themselves are fabricated.
