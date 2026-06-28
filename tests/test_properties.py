from hypothesis import given, settings, strategies as st

from generator import generate_matter, list_scenarios, project_to_canonical
from generator.schema import validate_canonical, validate_matter


@settings(max_examples=30, deadline=None)
@given(
    scenario=st.sampled_from(list_scenarios()),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
def test_generated_contracts_hold_for_arbitrary_seeds(scenario, seed):
    matter = generate_matter(scenario, seed)
    assert not validate_matter(matter)
    assert not validate_canonical(project_to_canonical(matter))
