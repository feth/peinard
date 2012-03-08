from decimal import Decimal

import peinard


def check_result(expected, result):
    """
    expected result may be unordered
    """
    assert len(expected) == len(result)
    for transfer in expected:
        assert transfer in result, "not fully reliable because of Decimal comparison"

def test_cases():
    result = peinard.heuristic(
        {"a": Decimal(-2),
        "b": Decimal(1),
        "c": Decimal(1)})
    expected = [('a', 'c', Decimal('1')), ('a', 'b', Decimal('1'))]
    check_result(expected, result)

    peinard.heuristic(
        {"a": Decimal(-1.1),
        "b": Decimal(0.1),
        "c": Decimal(1.0)})
    expected = [('a', 'c', Decimal('1')), ('a', 'c', Decimal('0.1'))]
    check_result(expected, result)
