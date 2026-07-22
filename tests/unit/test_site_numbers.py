from distributed_discovery.site.numbers import currency, expected_count, probability


def test_probability_pairs_readable_and_exact_values() -> None:
    presented = probability("223779310319051/333709716796875")
    assert presented.display == "67.1%"
    assert presented.exact == "223779310319051/333709716796875"
    assert presented.display in presented.accessible
    assert presented.exact in presented.accessible


def test_expected_count_rounds_without_losing_exact_value() -> None:
    presented = expected_count("4605284003019928/3243658447265625")
    assert presented.display == "1.42"
    assert presented.exact == "4605284003019928/3243658447265625"


def test_special_values_are_not_rendered_as_zero() -> None:
    assert probability(None).display == "Not applicable"
    assert expected_count("undefined").display == "Undefined"
    assert expected_count("infinity").display == "∞"
    assert expected_count("-inf").display == "−∞"


def test_currency_preserves_exact_source() -> None:
    presented = currency("7/4")
    assert presented.display == "$1.75"
    assert presented.exact == "7/4"
