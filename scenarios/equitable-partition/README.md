# Scenario: equitable-partition

A **Maine partition action among co-tenants** who inherited a single parcel as tenants
in common. One co-owner wants to cash out; the others want to keep the property in the
family. The court must choose between **partition in kind** and **partition by sale**,
sort out an **accounting** for taxes and upkeep among the co-tenants, and untangle an
**access / right-of-way wrinkle** that drives whether the land can fairly be divided
at all.

## Models

- **Practice area:** real_estate · **case_type:** `partition` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `RE`
- **Parties (4 + counsel):** `plaintiff` (co-tenant seeking partition/sale), `defendant`,
  `defendant_2`, `defendant_3` (co-tenants opposing the sale). The client is the
  `plaintiff`; `client_role: plaintiff` makes the plaintiff the signing filer.
  Demonstrates a multi-defendant roster of co-owners projecting through to the canonical
  case (each `defendant_N` projects via the schema's `additionalProperties`).

## Governing law

The issues are tied to the Maine partition statutes (`§` citations throughout):

- **Right to compel partition** among tenants in common — 14 M.R.S. § 6501.
- **Partition procedure / appointment of referees** — 14 M.R.S. Chapter 719.
- **Equitable partition** where physical division is impractical or would injure the
  co-owners — 14 M.R.S. § 6051(7).
- **Owelty** (an equalizing money payment) on an in-kind division.
- **Accounting** for taxes, upkeep, rents, and contributions among co-tenants.
- The **access / right-of-way** question and its effect on marketability and the
  feasibility of an in-kind division (also surfaced as a declaratory-judgment count).

## Facts that vary by seed

Property type and acreage, the ownership structure (`num_co_owners`), who they inherited
from and when, assessed value, the kind of partition sought, the improvements, the
nature of the `access_issue`, and a boolean `contribution_dispute`. The accounting and
access facts feed the disputed-facts list, the interview, and the litigation counts.

## Litigation depth (`litigation` block)

- **3 causes of action** (ordered, sequential counts): partition, accounting and
  contribution, and a declaratory judgment as to the right-of-way.
- **2–4 affirmative defenses** sampled by seed (fair in-kind division, set-off for
  exclusive use, a family agreement barring sale, laches).
- **One counterclaim** for an accounting and contribution by the opposing co-tenant.
- **2–4 motions** sampled by seed (appoint referees, partition by sale, an accounting,
  determine the access right) with dispositions.
- A chronologically-ordered **docket** (5 entries; non-overlapping date windows guarantee
  order): complaint, answers, appointment of referees, referees' report, and the hearing
  on sale vs. in kind.
- **trial** info (`jury: false`, estimated days, scheduled date) and `posture: pleadings`.
- **1–3 experts** (real estate appraiser and surveyor retained by the plaintiff, a
  forester on timber value retained by a defendant).

## Third parties, evidence, financials

- **3–5 third parties** drawn from a broker, the town assessor (`Town Assessor's Office`),
  a non-party sibling who claims to have paid the taxes, a mortgage-holding bank, a
  prospective buyer, and a licensed surveyor.
- **4–7 evidence items**: the recorded deed and chain of title, the probate decree, the
  tax assessment and bills, the appraisal and broker's opinion, the survey and subdivision
  sketch, records of taxes and upkeep paid, and photographs.
- **3–5 financials**: assessed/appraised value, estimated net sale proceeds, taxes and
  upkeep advanced, a proposed owelty payment, and brokerage/sale costs.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — example forms
`CV-001` (civil complaint) and `RE-PART` (partition).

## Reproduce

```sh
python3 tools/generate.py equitable-partition --seed 1
python3 tools/smoke.py --scenarios equitable-partition --count 8 -v
```

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
so count numbering and chronology stay coherent. `contribution_dispute` is a boolean fact,
so it is never used with the `{..._lower}` string helper, and no fact references another
fact.
