# Scenario: like-kind-exchange-1031

A smaller, tax-driven cousin of the sale binders: an **IRC § 1031 deferred like-kind
exchange**. A **qualified intermediary** holds the proceeds; the exchangor identifies
replacement property within **45 days** and closes within **180 days**, matching value and
debt to defer gain. Part of the real-estate & asset-sale closing suite.

## Models

- Practice area: tax · transactional (`assign_docket: false`)
- Parties: `exchangor`/taxpayer (the client), `relinquished_buyer` (buys the property being
  sold), and `replacement_seller` (sells the property being acquired)
- Rich `facts`: relinquished price/basis/debt, replacement price/debt, `exchange_type`,
  the relinquished-closing / 45-day `identification_deadline` / 180-day `exchange_deadline`
  / replacement-closing dates, `identification_rule` (three-property / 200% / 95%),
  `boot_risk`, and `related_party` status.
- `communications`: CPA's 1031 setup memo → QI's funds-received / deadlines letter →
  exchangor's 45-day identification notice → replacement closing (QI funds direction) →
  CPA's Form 8824 completion summary.

## Key issues

Qualified-intermediary safe harbor and non-receipt (`IRC § 1031`; `Treas. Reg.
§ 1.1031(k)-1`), the 45/180-day periods, boot and debt replacement (`§§ 1031(b), (d)`),
the related-party two-year rule (`§ 1031(f)`), and transfer tax on each leg.
