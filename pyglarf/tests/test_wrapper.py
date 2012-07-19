from nose.tools import assert_equal
from pyglarf import GlarfWrapper

test_sentences = ["Seven years after the bandages last came off, actor "
                  "Brendan Fraser returns in The Mummy: Tomb of the Dragon "
                  "Emperor as archaeologist Rick O'Connell, this time "
                  "retired, and with a grown-up son Alex.", "Hello, world."]


def test_split():
    """Test correct splitting of Glarf output

    This tests two particular cases: The first sentence failes with a Glarf
    output of ((***ERROR***)) whereas the second one gets parsed with a
    root element of ((NP, and might fool a naive split where ((S occurs."""

    with GlarfWrapper() as gw:
        plain, parsed, glarfed = gw.make_sentences(test_sentences)
    assert_equal(len(plain), 2)
    assert_equal(len(parsed), 2)
    assert_equal(len(glarfed), 2)
    assert_equal(glarfed[0], '((***ERROR***))')
