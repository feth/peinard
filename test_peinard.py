from decimal import Decimal

import peinard


def debug(expected, result, data):
    return """expected:
%s
got:
%s
Input data was:
%s""" % (expected, result, data)


def check_result(data, expected):
    """
    expected result may be unordered
    """
    result = peinard.heuristic(data)
    assert len(expected) == len(result), \
        "length don't match.\n%s" % debug(expected, result, data)

    for transfer in expected:
        assert transfer in result, \
            "not fully reliable because of Decimal comparison.\n%s" \
            % debug(expected, result, data)


def test_cases():
    data = {"a": Decimal(-2),
        "b": Decimal(1),
        "c": Decimal(1)}
    expected = [('a', 'c', Decimal('1')), ('a', 'b', Decimal('1'))]
    check_result(data, expected)

    data = {"a": Decimal(-1.1),
        "b": Decimal(0.1),
        "c": Decimal(1.0)}
    expected = [('a', 'c', Decimal('1')), ('a', 'c', Decimal('0.1'))]
    check_result(data, expected)
