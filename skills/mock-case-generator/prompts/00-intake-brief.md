# Prompt: Frame the matter

You are an intake attorney building a FICTIONAL test matter. From the brief below,
decide the frame. Keep it realistic for the jurisdiction.

BRIEF:
{brief}

Produce:
- `practice_area` (family | probate | tax | civil | criminal | business | real_estate | other)
- `case_type` (routing label, e.g. family_matters, decedent_estate, estate_tax, small_claims)
- `jurisdiction`: state, county, court_location, court_type
- `status` (intake | pre_filing | filed | active | closed)
- a one-sentence plain-language `matter.summary`
- the canonical party roles this matter needs (from: plaintiff, defendant, petitioner,
  respondent, decedent, personal_representative, attorney, other_party, company, child_N)
- which role is the represented `client`

Do not invent real people. Note any facts the brief leaves open that you will need to
fill in or flag as unknown.
