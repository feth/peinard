from peinard import heuristic, mkdec


def debug(msg, result):
    """
    convenience debug func for theses tests
    """
    return """%s
got:
%s""" % (msg, result)


def perform(data, expected):
    """
    expected result may be unordered
    """
    result = heuristic(data)
    assert len(expected) == len(result), debug("unmatched lengths", result)

    for transfer in expected:
        assert transfer in result, debug("not sure if fully reliable "
            "because of Decimal comparison.", result)


TEST_MATRIX = (
    (
        "null test",
        {},
        [],
    ),
    (
        "1 person, null test",
        {"a": mkdec(0)},
        [("a", None, mkdec(0))],
    ),
    (
        "2 persons, no decimals",
        {"a": mkdec(1),
        "b": mkdec(-1)},
        [("b", "a", mkdec(1))],
    ),
    (
        "2 persons, with decimals",
        {"a": mkdec(1.1),
        "b": mkdec(-1.1)},
        [("b", "a", mkdec(1.1))],
    ),
    (
        "3 persons, no decimals",
        {"a": mkdec(-2),
        "b": mkdec(1),
        "c": mkdec(1)},
        [('a', 'c', mkdec(1)), ('a', 'b', mkdec(1))]
    ),
    (
        "3 persons, with decimals",
        {"a": mkdec(-1.1),
        "b": mkdec(0.1),
        "c": mkdec(1.0)},
        ([('a', 'c', mkdec(1)), ('a', 'b', mkdec(0.1))])
    )
    )


def test_generator():
    """
    uses the TEST_MATRIX to test heuristic,
    assuming that it is a tuple of triples:
    -name of the test
    -input data
    -expected output.
    """
    for name, data, expected in TEST_MATRIX:
        test = lambda: perform(data, expected)
        test.description = '''%s
-input data: \t%s
-expected: \t%s''' % (name, data, expected)
        yield test
