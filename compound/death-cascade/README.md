# Compound: death-cascade

One death, three intertwined matters. Models how administering a decedent's estate
cascades across **probate**, **estate tax**, and a **guardianship** for a surviving minor.

| Local id | Scenario | Shared roles |
|----------|----------|--------------|
| `probate` | `decedent-estate-informal` | decedent, personal_representative (surviving spouse) |
| `estate_tax` | `estate-tax-706` | same decedent, same personal_representative |
| `guardianship` | `minor-guardianship` | grandparent (petitioner), surviving spouse (respondent), minor child (ward) |

**Through-line:** the decedent and personal representative are the *same people* in the
probate and the 706/706ME filings (the inventory and date-of-death values feed the tax
return), and the minor child is at once an **heir** of the estate and the **ward** of the
guardianship.

```bash
python tools/compound.py death-cascade --seed 1 --summary
```
