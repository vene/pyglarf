"""Extends nltk.Tree with some important utilitaies to navigate a Glarf tree"""

# Author: Vlad Niculae <vlad@vene.ro>
# License: BSD

import re
from nltk.tree import Tree

from pyglarf import Relation, NounPhrase

ptb_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD',
            'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB',
            'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN',
            'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
glarf_pos_tags = ptb_tags + ['|.|', '|,|', '$', '|#|', '|``|', "|''|", '|:|']
excluded_tags = glarf_pos_tags + ['EC-TYPE']

leaf_pattern = re.compile(""" \(NIL\)   | # The (NIL) marker is a leaf value
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
        return {tr.node: ' '.join(tr) for tr in filter(lambda t:
                                                isinstance(t, GlarfTree) and
                                                t.height() == 2 and
                                                t.node not in excluded,
                                                self)}

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
            result = res[0]
            # try to get its parent
            parent = self.parent(result)
            return parent if parent is not None else result
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

    def print_flat(self):
        if self.height() == 2:
            return '%s/%s' % (self[0], '+'.join(self[1:]))
        else:
            return ' '.join(leaf.print_flat() for leaf in self.ptb_leaves())

    def parent(self, subtree):
        # XXX: why can't we use trees with backlinks?
        try:
            return self.subtrees(lambda tr: subtree in tr).next()
        except StopIteration:
            return None

    def _build_np(self, np):
        """Construct an NP object"""
        head = np.head()
        name = []
        date = None
        attrs = np.attributes()
        subphrases = {}  # specifiers, complements and relative clauses
        links = {}  # apposites and affiliated links
        parent = self.subtrees(lambda tr: np in tr).next()
        role = parent.node

        # gather interesting attributes of the NP from its children
        for child in np:
            if isinstance(child, GlarfTree):
                # subtrees:
                if any(t in child.node for t in ('-POS', 'COMP', 'RELATIVE')):
                    subphrases[child.node] = child[0]

                # key fields
                elif child.node.startswith('NAME'):
                    name.append(child)
                elif child.node == 'REG-DATE':
                    date = child

                # links
                elif child.node in ('APPOSITE', 'AFFILIATED'):
                    links[child.node] = []
                    for idx in filter(lambda tr: tr.node.startswith('INDEX'),
                                      child[0]):
                        links[child.node].append(idx[0])

        return NounPhrase(head, role, name, date, subphrases, links, **attrs)

    def _build_rel(self, parent, pred):
        """Construct a relation from an appropriate Tree."""
        head = pred.head()
        attrs = pred.attributes()
        attrs['CATEGORY'] = pred.node
        attrs['PARENT_CATEGORY'] = parent.node
        base = attrs.pop('BASE', head[0][0])
        index = pred.head()[0][1]
        args = {}
        advs = {}
        support = []

        for tr in pred:
            if not isinstance(tr, GlarfTree):
                continue
            if tr.node.startswith('P-ARG'):
                if tr[0] == ' (NIL)':
                    args[tr.node] = ('NIL', 'NIL', [], [])
                    continue

                arg_type = tr[0].node
                args[tr.node] = ([], arg_type, [], [])
                ids = [k[1] for k in filter(lambda k: k[0].startswith('INDEX'),
                                            tr[0].attributes().items())]
                for id_nr in ids:
                    phrase = self.phrase_by_id(id_nr)
                    args[tr.node][0].append(phrase.node)
                    args[tr.node][2].append(id_nr)
                    args[tr.node][3].append(phrase)

                if len(ids) == 0 and any(t.node == 'TREE+INDEX'
                                         for t in tr[0]):
                    args[tr.node][0].append('TREE+INDEX currently unsupported')
                    args[tr.node][3].append(GlarfTree('', []))

            elif tr.node == 'P-SUPPORT':
                support_type = tr[0].node
                id_nr = tr[0][1][0]  # ugly but works
                phrase = self.phrase_by_id(id_nr)
                phrase_role = phrase.node
                support.append((phrase_role, support_type, id_nr, phrase))

        for tr in parent:
            if not isinstance(tr, GlarfTree):
                continue
            if tr.node.startswith('ADV'):
                ids = [k[1] for k in filter(lambda k: k[0].startswith('INDEX'),
                                            tr[0].attributes().items())]

                adv_id = ids.pop() if len(ids) > 0 else None
                advs[tr.node] = (tr[0].node, adv_id, tr[0])

        return Relation(index, base, args, support, advs, **attrs)

    def nps(self):
        is_np = lambda tr: tr.node == 'NP' and 'EC-TYPE' not in tr.daughters()
        return (self._build_np(np) for np in self.subtrees(is_np))

    def rels(self):
        with_args = lambda tr: any([daughter.startswith('P-ARG')
                                    for daughter in tr.daughters()])
        for pos in self.treepositions():
            if isinstance(self[pos], GlarfTree) and with_args(self[pos]):
                yield self._build_rel(self[pos[:-2]], self[pos])

    @classmethod
    def glarf_parse(cls, s):
        return cls.parse(s, leaf_pattern=leaf_pattern,
                          remove_empty_top_bracketing=True)
