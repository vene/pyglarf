from StringIO import StringIO


def _flat_list(l):
    if l is None or len(l) == 0:
        return None
    elif isinstance(l, str):
        return l
    else:
        return ' '.join(elem.print_flat() for elem in l)


class NounPhrase(object):
    """Describes an NP."""
    def __init__(self, head, role, name, date, subphrases, links, **kwargs):
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
        # TODO: conjunctions/disjunctions?

    def __repr__(self):
        repr = StringIO()
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, '%s [%s]' % (self.role, attrs_repr)
        print >> repr, 'HEAD: %s' % _flat_list(self.head)
        if self.head is not None:
            print >> repr, 'RECURSIVE_HEAD: %s' % _flat_list(self.rec_head_)
        print >> repr, 'NAME: %s' % _flat_list(self.name)
        print >> repr, 'DATE: %s' % self.date
        for tag, indices in sorted(self.links.items()):
            print >> repr, '%s: %s' % (tag, '+'.join(indices))

        for tag, tree in sorted(self.subphrases.items()):
            print >> repr, '%s [%s]: %s' % (tag, tree.node, tree.print_flat())
        return repr.getvalue()
