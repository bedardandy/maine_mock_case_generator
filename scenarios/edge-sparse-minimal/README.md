# Scenario: edge-sparse-minimal

**Edge-case pack — sparseness stress.** A bare-bones collections matter where everything
optional is absent, yet the matter remains fully schema-valid.

## What it smoke-tests downstream

- **Organization-only parties** with *no* address, phone, email, DOB, or SSN — catches
  fillers that dereference contact fields without checking presence.
- **No attorney block** (an unrepresented entity) — catches signature blocks and
  service-list logic that assume counsel.
- **No interview, objectives, third parties, experts, financials, communications, or
  litigation sections** — catches consumers that iterate sections without guarding.
- **A two-key `facts` block** — catches mappings that expect a rich facts namespace and
  should degrade to blank fields, not errors.
- **No `event_date`** — only a filing date exists.

Pairs with `pro-se-interstate-custody` (sparse person) as the organizational analogue.
