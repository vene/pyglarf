import StringIO


class Predicate(object):
    """Wrapper object for a predicate to allow for easier querying.

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
    def __init__(self, index, head='?', args=None, support=None,
                 flat_repr=True, **kwargs):
        self.index = index
        self.head = head
        self.args = args
        self.support = support
        self.attrs = kwargs
        self.flat_repr = flat_repr

    def __repr__(self):
        """Returns a string representation of the predicate."""
        repr = StringIO.StringIO()
        attrs_repr = ', '.join(['%s: %s' % it for it in self.attrs.items()])
        print >> repr, '%s/%s [%s]' % (self.head, self.index, attrs_repr)

        for tag, sup_tree in self.support:
            print >> repr, '\tP-SUPPORT [%s]: %s' % (tag,
                        sup_tree.print_flat() if self.flat_repr else sup_tree)
        for arg, (arg_type, arg_id, arg_trees) in sorted(self.args.items()):
            print >> repr, '\t%s [%s INDEX: %s]: ' % (arg, arg_type,
                                                   '+'.join(arg_id)),

            for arg_tree in arg_trees:
                if self.flat_repr:
                    print >> repr, arg_tree.print_flat()
                else:
                    print >> repr, arg_tree
                    print >> repr

        return repr.getvalue()
