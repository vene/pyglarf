"""Extends nltk.Tree with some important utilitaies to navigate a Glarf tree"""

# Author: Vlad Niculae <vlad@vene.ro>
# License: BSD

import re
from collections import defaultdict

# backport
try:
    from nltk.tree import Tree
except ImportError:
    from .nltkbackports import Tree

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
    def __init__(self, *args, **kwargs):
        Tree.__init__(self, *args, **kwargs)
        self._forest = None
        self._tuples = None

    def daughters(self):
        """Get the tags of all direct descendants of the tree"""
        return (tr.node if isinstance(tr, Tree) else tr for tr in self)

    def attributes(self, excluded=excluded_tags):
        """Return all attribute leaves of a subtree, as a Python dictionary"""
        return dict([(tr.node, ' '.join(tr)) for tr in filter(lambda t:
                                                isinstance(t, GlarfTree) and
                                                t.height() == 2 and
                                                t.node not in excluded,
                                                self)])

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

    def index(self):
        for subtr in self:
            if isinstance(subtr, Tree) and subtr.node == 'INDEX':
                return subtr[0]
        for subtr in self:
            if isinstance(subtr, Tree) and subtr.node == 'HEAD':
                return subtr.index()
        return 'leaf' + '+'.join(self.ptb_leaves().next()[2:])
        return None

    def most_specific_head(self):
        head = self[0].head()
        if not head:
            return self
        else:
            return head.most_specific_head()

    def head_by_id(self, id_nr):
        phrase = self.phrase_by_id(id_nr)
        if not phrase:
            return ''
        else:
            return phrase.most_specific_head()

    def cat_range(self):
        """Returns the struture representation: ROLE START-END"""
        leaves = [k for ks in self.ptb_leaves() for k in ks[1:]]
        if not leaves:
            return ''
        elif self.height() == 2:
            return '%s %s-%s' % (self.node, leaves[1], leaves[-1])
        else:
            return '%s+%s %s-%s' % (self.node, self[0].node, leaves[1],
                                    leaves[-1])

    def print_flat(self, indices=True, lemma=True, pos=True, structure=True):
        if self.height() == 2:
            if self.node in glarf_pos_tags:
                my_form, my_lemma = self[:2]
                my_idx = self[2:]
                output = str(my_form)
                if lemma:
                    output += '/%s' % my_lemma
                if pos:
                    output += '/%s' % self.node
                if indices:
                    # ex.: John/1, or: "put off"/5+6
                    output += '/%s' % '+'.join(my_idx)
            else:
                output = ''
        else:
            output = ' '.join(leaf.print_flat(indices, lemma, pos, structure)
                              for leaf in self.ptb_leaves())
            if structure:
                output += ' (%s)' % ', '.join(filter(lambda x: x,
                                              (t.cat_range() for t in self)))
        return output

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
        conj = []
        date = None
        attrs = np.attributes()
        index = attrs.get('INDEX', None)
        if index is None:
            index = np.index()
        subphrases = {}  # specifiers, complements and relative clauses
        links = {}  # apposites and affiliated links
        parent = self.subtrees(lambda tr: np in tr).next()
        role = parent.node

        # gather interesting attributes of the NP from its children
        for child in np:
            if isinstance(child, GlarfTree):
                # subtrees:
                if any(t in child.node for t in ('-POS', 'COMP', 'RELATIVE',
                                                 'ADV')):
                    subphrases[child.node] = child[0]

                # key fields
                elif child.node.startswith('NAME'):
                    if child[0].node == 'PP':
                        subphrases[child.node] = child[0]
                    else:
                        name.append(child)
                elif child.node == 'REG-DATE':
                    date = child
                elif child.node.startswith('CONJ') and \
                     not child.node.startswith('CONJOINED'):
                    conj.append(child)

                # links
                elif child.node in ('APPOSITE', 'AFFILIATED'):
                    links[child.node] = [idx[0] for idx in child[0]
                                         if idx.node.startswith('INDEX')]

        return NounPhrase(index, head, role, name, conj, date, subphrases,
                          links, np.print_flat(), **attrs)

    def _build_rel(self, parent, pred):
        """Construct a relation from an appropriate Tree."""
        head = pred.head()
        attrs = pred.attributes()
        attrs['CATEGORY'] = pred.node
        attrs['PARENT_CATEGORY'] = parent.node
        attrs['FORM'] = head[0][0]
        base = attrs.pop('BASE', head[0][0])
        aux = {}
        index = '+'.join(head[0][2:])
        args = {}
        advs = {}
        support = []

        for tr in pred:
            if not isinstance(tr, GlarfTree):
                continue
            if tr.node.startswith('AUX'):
                aux[tr.node] = tr

            if tr.node.startswith('P-ARG'):
                if tr[0] == ' (NIL)':
                    args[tr.node] = ('NIL', 'NIL', [], [])
                    continue

                arg_type = tr[0].node
                args[tr.node] = ([], arg_type, [], [])
                ids = [k[1]
                       for k in tr[0].attributes().items()
                       if k[0].startswith('INDEX')]
                ids.extend([k[1].strip('|').split('+')
                            for k in tr[0].attributes().items()
                            if k[0] == 'TREE+INDEX'])

                for id_nr in ids:
                    if isinstance(id_nr, str):
                        phrase = self.phrase_by_id(id_nr)
                    elif isinstance(id_nr, list):
                        if self._forest is not None:
                            phrase = self._forest.phrase_by_id(*id_nr)
                            if not phrase:
                                continue
                        else:
                            phrase = GlarfTree('**WARNING**', [
                                'TREE+INDEX is only supported if you parse '
                                'the entire forest with GlarfForest.'])
                        id_nr = '/'.join(id_nr)
                    else:
                        raise ValueError('Invalid INDEX in argument.')

                    args[tr.node][0].append(phrase.node)
                    args[tr.node][2].append(id_nr)
                    args[tr.node][3].append(phrase)

            elif tr.node == 'P-SUPPORT':
                support_type = tr[0].node
                id_nr = tr[0][1][0]  # ugly but works
                phrase = self.phrase_by_id(id_nr)
                phrase_role = phrase.node
                support.append((phrase_role, support_type, id_nr, phrase))

        for tr in parent:
            if not isinstance(tr, GlarfTree):
                continue
            if any(tr.node.startswith(tag) for tag in ('ADV', 'OBJ', 'PRD',
                                                       'L-SBJ', 'PRT')):
                ids = [k[1] for k in filter(lambda k: k[0].startswith('INDEX'),
                                            tr[0].attributes().items())]

                adv_id = ids.pop() if len(ids) > 0 else None
                advs[tr.node] = (tr[0].node, adv_id, tr[0])

        return Relation(index, base, aux, args, support, advs, **attrs)

    def nps(self):
        is_np = lambda tr: tr.node == 'NP' and 'EC-TYPE' not in tr.daughters()
        return ((self._build_np(np), np) for np in self.subtrees(is_np))

    def entities(self):
        """Extracts NPs and builds a dictionary of entity-attributes"""
        entities = defaultdict(list)
        nps_by_id = {}
        entities = {}
        for np, _ in self.nps():
            idx = np.index
            nps_by_id[idx] = np
            entities[idx] = np.short_repr(), []

        for idx, np in nps_by_id.items():
            #print "***"
            #print np.short_repr()
            #if len(np.name) > 0:
            #    key = _flat_list(np.name, indices=False)
            #    entities[key].extend(
            #        attr.print_flat(indices=False)
            #        for attr in np.subphrases.values()
            #    )
            #elif np.head is not None:
            # Take the linked np with the most semantic info (???)
            linked_structures = [nps_by_id.get(sub_idx)
                                 for _, indices in np.links.items()
                                 for sub_idx in indices]
            linked_structures.append(np)
            linked_structures = filter(lambda x: x is not None, linked_structures)

            # score counts the amount of semantic info, I hope
            score = lambda np: len(filter(lambda (key, val):
                                   key == 'PATTERN' and val == 'NAME' or
                                   key == 'SEM-FEATURE' or
                                   key == 'NE-TYPE',
                                   np.attrs.items()))

            linked_structures = sorted(linked_structures, key=score)
            best = linked_structures[-1]
            key = best.index
            if key == idx:
                entities[key][1].extend(attr.print_flat(indices=False, lemma=False, pos=False, structure=False)
                                        for apos in linked_structures[:-1]
                                        for attr in apos.subphrases.values())
            else:
                head = np.head
                while isinstance(head, GlarfTree) and head.height() > 2:
                    entities[key][1].append(head.print_flat(indices=False, lemma=False, pos=False, structure=False))
                    head = head[0].head()

            entities[key][1].extend(attr.print_flat(indices=False, lemma=False, pos=False, structure=False)
                                    for attr in np.subphrases.values()
            )
        return entities

    def rels(self):
        with_args = lambda tr: any([daughter.startswith('P-ARG')
                                    for daughter in tr.daughters()])
        for pos in self.treepositions():
            if isinstance(self[pos], GlarfTree) and with_args(self[pos]):
                yield self._build_rel(self[pos[:-2]], self[pos])

    def _initialize_tuples(self, raw_tuples_list):
        """Parse Glarf tuple file and use the information from it"""
        self._tuples = [tuple(val.strip() for val in t.split('|'))
                        for t in raw_tuples_list] if raw_tuples_list else []
        return self

    def _set_lemmas(self):
        lemmas = {}
        for t in self._tuples:
            lemmas[t[7]] = t[9]
            lemmas[t[19]] = t[21]
        for token in self.ptb_leaves():
            lemma = lemmas.get(token[1], '').lower()
            token.insert(1, lemma)
        return self

    @classmethod
    def glarf_parse(cls, s, raw_tuples_list=None):
        tree = cls.parse(s, leaf_pattern=leaf_pattern,
                         remove_empty_top_bracketing=True)
        if tree.node == '***ERROR***':
            raise ValueError('Glarf string resulted from parsing failure')

        tree._initialize_tuples(raw_tuples_list)
        tree._set_lemmas()
        return tree
