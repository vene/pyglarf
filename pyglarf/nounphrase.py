from StringIO import StringIO


def _flat_list(l, indices=True, structure=True):
    if l is None or len(l) == 0:
        return None
    elif isinstance(l, str):
        return l
    else:
        return ' '.join(elem.print_flat(indices, structure) for elem in l)


class NounPhrase(object):
    """Describes an NP."""
    def __init__(self, index, head, role, name, conj, date, subphrases, links,
                 full_flat, **kwargs):
        assert index is not None
        self.index = index
        self.head = head
        self.role = role
        self.name = name
        self.conj = conj
        self.date = date
        self.subphrases = subphrases
        self.links = links
        self.full_flat = full_flat
        self.attrs = kwargs

        # Calculated attributes
        if self.head:
            self.rec_head_ = self.head.most_specific_head()
            assert self.rec_head_.index is not None

        if self.conj:
            self.rec_conj_ = []
            for t in self.conj:
                if t.node.startswith('CONJUNCTION'):
                    self.rec_conj_.append(t[0])
                elif t.node.startswith('CONJ'):
                    self.rec_conj_.append(t[0].head().most_specific_head()
                                          if t[0].head() is not None
                                          else t[0])

    def __repr__(self):
        repr = StringIO()
        print >> repr, self.full_flat
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, '%s [%s]' % (self.role, attrs_repr)
        if self.conj:
            for t in self.conj:
                print >> repr, '%s: %s' % (t.node, t.print_flat())
            print >> repr, 'CONJ_REC_HEADS: %s' % _flat_list(self.rec_conj_)
        print >> repr, 'HEAD: %s' % _flat_list(self.head)
        if self.head is not None:
            print >> repr, 'RECURSIVE_HEAD: %s' % _flat_list(self.rec_head_)
        print >> repr, 'NAME: %s' % _flat_list(self.name)
        print >> repr, 'DATE: %s' % (self.date[0] if self.date else None)
        for tag, indices in sorted(self.links.items()):
            print >> repr, '%s: %s' % (tag, '+'.join(indices))

        for tag, tree in sorted(self.subphrases.items()):
            print >> repr, '%s [%s]: %s' % (tag, tree.node, tree.print_flat())
        return repr.getvalue()

    def short_repr(self):
        if self.name:
            return _flat_list(self.name, indices=False, structure=False)
        elif self.head:
            return _flat_list(self.head, indices=False, structure=False)
        elif self.date:
            return self.date[0]
        elif self.conj:
            return _flat_list(self.rec_conj_, indices=False, structure=False)
        else:
            return None
