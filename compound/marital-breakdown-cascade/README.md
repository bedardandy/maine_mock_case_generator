# Compound: marital-breakdown-cascade

A failing marriage, three intertwined matters: a **divorce**, a **protection-from-abuse**
order, and a dispute over the **marital business**.

| Local id | Scenario | Shared roles |
|----------|----------|--------------|
| `divorce` | `family-divorce-cumberland` | spouse_a (plaintiff), spouse_b (defendant), two children |
| `protection_order` | `protection-from-abuse` | same spouses, same children |
| `business_matter` | `business-formation-scorp` | spouse_b (applicant/owner), the marital business (company) |

**Through-line:** the same two spouses and the same two children appear in both the divorce
and the protection order (which shapes the parenting schedule), while the business run by
spouse_b is a marital asset whose value is contested in the divorce.

```bash
python tools/compound.py marital-breakdown-cascade --seed 1 --summary
```
