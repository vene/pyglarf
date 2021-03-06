import StringIO


class Relation(object):
    """Wrapper object for a relation to allow for easier querying.

    Relations are subtrees that directly dominate an object with args.

    TODO: for the moment only implements __repr__

    Attributes:
    -----------
    index, string (maybe make it int?):
        the unique identifier of the predicate within the sentence

    head, string:
        the representation of the head of the relation, normalized by GLARF.

    args, dict of Trees
        Normalized arguments in the form of lists of `Tree` objects.

    flat_repr, boolean, default=True:
        Whether to represent arguments as flat word/index strings or as trees.

    attrs, dict:
        Any supplementary extracted attributes such as word sense or voice.
    """
    def __init__(self, index, head=None, aux=None, args=None, support=None,
                 advs=None, flat_repr=True, **kwargs):
        self.index = index
        self.head = head
        self.aux = aux
        self.args = args
        self.support = support
        self.advs = advs
        self.attrs = kwargs
        self.flat_repr = flat_repr

    def __str__(self):
        """Returns a string representation of the predicate."""
        repr = StringIO.StringIO()
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, '%s/%s [%s]' % (self.head, self.index, attrs_repr)
        # show auxilliaries if exist:
        if self.aux:
            for node, tree in self.aux.items():
                print >> repr, '%s: %s' % (node,
                                           tree.print_flat(structure=False)
                                           if self.flat_repr else tree)
        # show supports
        for role, tag, sid, sup_tree in self.support:
            print >> repr, 'P-SUPPORT [%s %s INDEX: %s]: %s' % (role, tag, sid,
                        sup_tree.print_flat() if self.flat_repr else sup_tree)

        # show arguments
        for arg, (roles, arg_type, arg_id, trees) in sorted(self.args.items()):
            print >> repr, '%s [%s %s INDEX: %s]: ' % (arg, '+'.join(roles),
                                                       arg_type,
                                                       '+'.join(arg_id)),

            for arg_tree in trees:
                print >> repr, (arg_tree.print_flat()
                                if self.flat_repr else arg_tree)

        # show adverbs
        for adv, (adv_type, adv_id, tree) in sorted(self.advs.items()):
            print >> repr, '%s [%s INDEX: %s]: %s' % (adv, adv_type, adv_id,
                           tree.print_flat() if self.flat_repr else tree)
        return repr.getvalue()

    def __repr__(self):
        repr_dict = dict([(key, val.__repr__())
                         for key, val in self.__dict__.items()])
        return ("""Relation(index=%(index)s, head=%(head)s, aux=%(aux)s, \
args=%(args)s, support=%(support)s, advs=%(advs)s, flat_repr=%(flat_repr)s, \
**%(attrs)s)""" % repr_dict)
