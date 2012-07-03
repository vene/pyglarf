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
    def __init__(self, head, name, date, poses, comps, apposite=None,
                 affiliated=None, **kwargs):
        self.head = head
        self.name = name
        self.date = date
        self.poses = poses
        self.comps = comps
        self.apposite = apposite
        self.affiliated = affiliated
        self.attrs = kwargs

    def __repr__(self):
        repr = StringIO()
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, 'NP [%s]' % attrs_repr
        print >> repr, 'HEAD: %s' % _flat_list(self.head)
        print >> repr, 'NAME: %s' % _flat_list(self.name)
        print >> repr, 'DATE: %s' % self.date
        if self.apposite:
            print >> repr, 'APPOSITE: %s' % '+'.join(self.apposite)
        if self.affiliated:
            print >> repr, 'AFFILIATED: %s' % '+'.join(self.affiliated)
        for pos, tree in (sorted(self.poses.items()) +
                         sorted(self.comps.items())):
            print >> repr, '%s: %s' % (pos, tree.print_flat())
        return repr.getvalue()
