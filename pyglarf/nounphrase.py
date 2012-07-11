from StringIO import StringIO


def _flat_list(l, indices=True):
    if l is None or len(l) == 0:
        return None
    elif isinstance(l, str):
        return l
    else:
        return ' '.join(elem.print_flat(indices) for elem in l)


class NounPhrase(object):
    """Describes an NP."""
    def __init__(self, index, head, role, name, date, subphrases, links,
                 **kwargs):
        assert index is not None
        self.index = index
        self.head = head
        self.role = role
        self.name = name
        self.date = date
        self.subphrases = subphrases
        self.links = links
        self.attrs = kwargs

        # Calculated attributes
        if self.head is not None:
            self.rec_head_ = self.head.most_specific_head()
            assert self.rec_head_.index is not None
        # TODO: conjunctions/disjunctions?

    def __repr__(self):
        repr = StringIO()
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, '%s [%s]' % (self.role, attrs_repr)
        print >> repr, 'HEAD: %s' % _flat_list(self.head)
        if self.head is not None:
            print >> repr, 'RECURSIVE_HEAD: %s' % _flat_list(self.rec_head_)
        print >> repr, 'NAME: %s' % _flat_list(self.name)
        print >> repr, 'DATE: %s' % self.date[0] if self.date else None
        for tag, indices in sorted(self.links.items()):
            print >> repr, '%s: %s' % (tag, '+'.join(indices))

        for tag, tree in sorted(self.subphrases.items()):
            print >> repr, '%s [%s]: %s' % (tag, tree.node, tree.print_flat())
        return repr.getvalue()

    def short_repr(self):
        if len(self.name) > 0:
            return _flat_list(self.name, indices=False)
        elif self.head is not None:
            return _flat_list(self.head, indices=False)
        elif self.date is not None:
            return self.date[0]
        else:
            return None
