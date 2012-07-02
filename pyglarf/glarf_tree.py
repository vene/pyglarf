"""Extends nltk.Tree with some important utilitaies to navigate a Glarf tree"""

# Author: Vlad Niculae <vlad@vene.ro>
# License: BSD

import re
from nltk.tree import Tree

from pyglarf import Predicate

ptb_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD',
            'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB',
            'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN',
            'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
glarf_pos_tags = ptb_tags + ['|.|', '|,|']
excluded_tags = glarf_pos_tags + ['EC-TYPE']

leaf_pattern = re.compile("""#\(NIL\)    | # The (NIL) marker is a leaf value
                             ".*?"      | # "Quoted strings" are leaf values
                             \|.*?\|    | # | barred stuff | are leaf values
                             [^\s\(\)]+'  # and everything else gets broken
                          """, re.X)

leaf_pattern = ' \(NIL\)|".*?"|\|.*?\||[^\s\(\)]+'


class GlarfTree(Tree):
    def daughters(self):
        """Get the tags of all direct descendants of the tree"""
        return (tr.node if isinstance(tr, Tree) else tr for tr in self)

    def attributes(self, excluded=excluded_tags):
        """Return all attribute leaves of a subtree, as a Python dictionary"""
        return {tr.node: ' '.join(tr) for tr in self.subtrees(lambda t:
                                                       t.height() == 2 and
                                                       t.node not in excluded)}

    def ptb_leaves(self, included=glarf_pos_tags):
        return self.subtrees(lambda t: t.height() == 2 and t.node in included)

    def phrase_by_id(self, id_nr):
        res = self.subtrees(lambda tr: any((isinstance(subtr, Tree)
                                                  and subtr.node == 'INDEX'
                                                  and subtr[0] == id_nr
                                                  for subtr in tr))
                                       and not any((isinstance(subtr, Tree)
                                                  and subtr.node == 'EC-TYPE'
                                                  for subtr in tr)))
        res = list(res)
        if len(res) == 1:
            return res[0]
        elif len(res) > 1:
            return GlarfTree('', res)
        else:
            return None

    def head(self):
        for subtr in self:
            if isinstance(subtr, Tree) and subtr.node == 'HEAD':
                return subtr
        return None

    def most_specific_head(self):
        head = self.head()
        if not head:
            return self
        else:
            return head.most_specific_head()

    def head_by_id(id_nr):
        phrase = self.phrase_by_id(id_nr)
        if not phrase:
            return ''
        else:
            return phrase.most_specific_head()

    def format_leaf(self):
        # assume this is a leaf, might crash otherwise
        return '%s/%s' % (self[0], '+'.join(self[1:]))

    def _build_pred(self, pred):
        """Construct a predicate from an appropriate Tree."""
        head = pred.head()
        attrs = pred.attributes()
        base = attrs.pop('BASE', head[0][0])
        index = pred.head()[0][1]
        args = {}

        for arg in pred:
            if not isinstance(arg, Tree) or not arg.node.startswith('P-ARG'):
                continue
            args[arg.node] = []
            ids = (k[1] for k in filter(lambda k: k[0].startswith('INDEX'),
                                        arg.attributes().items()))
            for id_nr in ids:
                args[arg.node].append(self.phrase_by_id(id_nr))
        #raise Exception
        return Predicate(index, base, args, **attrs)

    def predicates(self):
        with_args = lambda tr: any([daughter.startswith('P-ARG')
                                    for daughter in tr.daughters()])
        return (self._build_pred(pred) for pred in self.subtrees(with_args))

    @classmethod
    def glarf_parse(cls, s):
        return cls.parse(s, leaf_pattern=leaf_pattern,
                          remove_empty_top_bracketing=True)
