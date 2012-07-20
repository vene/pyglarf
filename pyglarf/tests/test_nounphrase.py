from nose.tools import assert_equal
# My wife, Mary, is beautiful.

from pyglarf import GlarfTree
apposite = GlarfTree('S', [GlarfTree('S-SBJ', [GlarfTree('NP', [GlarfTree(
                      'HEAD', [GlarfTree('NP', [GlarfTree('T-POS', [GlarfTree(
                      'PRP$', ['My', '0'])]), GlarfTree('HEAD', [GlarfTree(
                      'NN', ['wife', '1'])]), GlarfTree('PTB2-POINTER', [
                      '|0+1|'])])]), GlarfTree('PUNCTUATION', [GlarfTree('|,|',
                      ['|,|', '2'])]), GlarfTree('APPOSITE', [GlarfTree('NP',
                      [GlarfTree('NAME', [GlarfTree('NNP', ['Mary', '3'])]),
                      GlarfTree('PTB2-POINTER', ['|3+1|']), GlarfTree(
                      'SEM-FEATURE', ['NHUMAN']), GlarfTree('NE-TYPE', [
                      'PERSON']), GlarfTree('PATTERN', ['NAME']), GlarfTree(
                      'INDEX', ['5'])])]), GlarfTree('PTB2-POINTER', ['|0+2|']
                      ), GlarfTree('INDEX', ['4'])])]), GlarfTree(
                      'PUNCTUATION1', [GlarfTree('|,|', ['|,|', '4'])]),
                      GlarfTree('PRD', [GlarfTree('VP', [GlarfTree('L-SBJ', [
                      GlarfTree('NP', [GlarfTree('EC-TYPE', ['INF']),
                      GlarfTree('INDEX', ['4'])])]), GlarfTree('HEAD', [
                      GlarfTree('VG', [GlarfTree('HEAD', [GlarfTree('VBZ', [
                      'is', '5'])]), GlarfTree('P-ARG2', [GlarfTree('ADJP', [
                      GlarfTree('EC-TYPE', ['PB']), GlarfTree('INDEX', ['7'])])
                      ]), GlarfTree('P-ARG1', [GlarfTree('NP', [GlarfTree(
                      'EC-TYPE', ['PB']), GlarfTree('INDEX', ['4'])])]),
                      GlarfTree('INDEX', ['6']), GlarfTree('BASE', ['BE']),
                      GlarfTree('VERB-SENSE', ['1']), GlarfTree('SENSE-NAME', [
                      '"COPULA"'])])]), GlarfTree('PRD', [GlarfTree('ADJP', [
                      GlarfTree('HEAD', [GlarfTree('JJ', ['beautiful', '6'])]),
                      GlarfTree('PTB2-POINTER', ['|6+1|']), GlarfTree('INDEX',
                      ['7'])])]), GlarfTree('PTB2-POINTER', ['|5+1|']),
                      GlarfTree('TRANSPARENT', ['T'])])]), GlarfTree(
                      'PUNCTUATION2', [GlarfTree('|.|', ['|.|', '7'])]),
                      GlarfTree('PTB2-POINTER', ['|0+3|']), GlarfTree(
                      'TREE-NUM', ['0']), GlarfTree('FILE-NAME', ['"tmp"']),
                      GlarfTree('INDEX', ['0']), GlarfTree('SENTENCE-OFFSET',
                      ['0'])])

nps = [np for np, _ in apposite.nps()]


def test_correct_nps():
    assert_equal(nps[0].head.print_flat(indices=False, structure=False),
                 'My wife')
    assert_equal(nps[1].head.print_flat(indices=False, structure=False),
                 'wife')
    assert_equal(nps[2].name[0].print_flat(indices=False, structure=False),
                 'Mary')


def test_apposite():
    assert_equal(nps[0].links['APPOSITE'][0], nps[2].index)
