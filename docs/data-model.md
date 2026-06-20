# Data model

Two schemas, with a one-way projection between them.

## 1. Mock Matter — `catalog/mock_matter.schema.json`

The rich superset the generator produces. Required: `schema_version`, `provenance`,
`matter`, `parties`, `fact_pattern`.

| Section | What it holds |
|---------|---------------|
| `provenance` | `mock`/`fictional` flags, generator, version, `scenario_id`, `seed`, optional `model`. |
| `matter` | `matter_id`, `practice_area`, `title`, `jurisdiction{state,county,court_location,court_type}`, `case_type`, `docket_number`, `filing_date`, `event_date`, `status`, `summary`. |
| `parties` | Role-keyed party objects: `plaintiff`, `defendant`, `petitioner`, `respondent`, `decedent`, `personal_representative`, `attorney`, `other_party`, `company`, `client`, and `child_1..N`. |
| `third_parties[]` | Witnesses, institutions, agencies, experts-as-people: `{id,name,type,role,relationship,contact,description,relevance}`. |
| `fact_pattern` | `summary`, `narrative`, `undisputed_facts[]`, `disputed_facts[]`, `timeline[{date,event}]`. |
| `intake_interview` | `interviewer`, `interviewee_role`, `date`, `exchanges[{topic,question,answer,follow_up}]`. |
| `client_objectives` | `goals[]`, `priorities[]`, `constraints{budget,timeline,other}`, `risk_tolerance`, `desired_outcomes[]`, `non_starters[]`. |
| `issues[]` | `{id,issue,category,governing_law,sub_questions[],client_position,strength,notes}`. |
| `expert_opinions[]` | `{id,expert{name,field,credentials,retained_by},topic,opinion,basis,exhibits[]}`. |
| `evidence[]` | `{id,title,type,description,date,source,party}`. |
| `financials` | `currency`, `amounts[{label,amount,basis}]`, `total_claimed`. |
| `facts` | **Flat, form-specific canonical keys** (the bridge — see below). |

### Party object
`entity_type` (person/organization), `full_name` **or** `first_name`/`middle_name`/
`last_name`, `organization_name`, `role`, `address`/`city`/`state`/`zip`, `phone`,
`email`, `date_of_birth`, `ssn_last4`, `signature`, `bar_number`, `description`.
Provide `full_name` alone (downstream derives the parts) or the components.

## 2. Canonical Case — `catalog/canonical_case.schema.json`

A **vendored copy** of the contract the downstream form repos consume. Keep it in sync
with upstream `maine-court-forms/catalog/canonical_case.schema.json`.

```json
{
  "matter":   { "docket_number","case_id","court_county","court_location","court_type","case_type","filing_date","event_date" },
  "parties":  { "plaintiff": {party}, "defendant": {party}, "attorney": {party}, "child_1": {party}, "other_party": {party}, ... },
  "party":    {party},        // the signing filer
  "facts":    { ... }          // form-specific keys, passed through
}
```

## Projection (`project_to_canonical`)

| Mock Matter | → | Canonical Case |
|-------------|---|----------------|
| `matter.jurisdiction.county` | → | `matter.court_county` |
| `matter.matter_id` | → | `matter.case_id` |
| `matter.{docket_number,court_location,court_type,case_type,filing_date,event_date}` | → | same under `matter` |
| `parties.<role>` (canonical roles + `child_N`) | → | `parties.<role>`, reduced to canonical party fields |
| `parties.client` (or plaintiff/petitioner/PR) | → | `party` (signing filer) |
| `facts` | → | `facts` (unchanged) |

Notes:
- Non-canonical party fields (`role`, `entity_type`, `description`, `ssn_last4`,
  `organization_name`) are dropped; organizations keep their name in `full_name`.
- Aliases are added when helpful: `petitioner → plaintiff`, `respondent → defendant`,
  so strict downstream fillers that expect plaintiff/defendant still work.
- `client` is intentionally **not** projected as a party — it becomes `party`.

## The `facts` bridge

`facts` is where practice-area form fields live. Examples by scenario:
- family/divorce: `marriage_date`, `grounds`, `num_minor_children`, `separation_date`
- probate: `date_of_death`, `will_exists`, `approximate_estate_value`, `num_heirs`
- business: `entity_name`, `state_of_incorporation`, `s_corp_election`, `naics_code`
- estate tax: `gross_estate_value`, `marital_deduction`, `executor_name`, `return_due_date`

Downstream `mapping.json` files translate these keys to specific PDF field ids.
