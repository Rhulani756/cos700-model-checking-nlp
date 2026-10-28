from pipeline.nlp.prompt_builder import PromptBuilder
from pipeline.nlp.schemas import Counterexample


EXPECTED_GUIDANCE = {
    "array_bounds": "valid indices 0 through N - 1",
    "null_safety": "pointer that is dereferenced without being proven valid",
    "loop_termination": "configured unwind bound",
    "division_by_zero": "expression used as the divisor",
}


def make_counterexample(violation_type: str) -> Counterexample:
    return Counterexample.model_validate(
        {
            "violation_type": violation_type,
            "tool": "cbmc",
            "message": "test violation",
            "file": "submission.cpp",
            "line": 1,
            "trace": [],
        }
    )


def test_each_property_prompt_is_loaded_into_the_user_prompt() -> None:
    builder = PromptBuilder()

    for violation_type, expected_text in EXPECTED_GUIDANCE.items():
        counterexample = make_counterexample(violation_type)
        _, user_prompt = builder.build(counterexample)

        assert expected_text in user_prompt
        assert '<property_guidance>' in user_prompt
        assert '</property_guidance>' in user_prompt