from pyglarf import GlarfTree
import warnings

class GlarfForest(list):
    """A forest of GlarfTrees

    GlarfForest implements a frendlier interface than building GlarfTrees
    individually. Trees in a forest have a backlink for solving cross-sentence
    arguments.

    Parameters
    ----------

    glarf_parses: list of strings,
        List of Glarf output strings with which to build the forest. This
        is the third return value of GlarfWrapper.make_* functions.
    """

    def __init__(self, glarf_parses):
        for s in glarf_parses:
            tree = GlarfTree.glarf_parse(s)
            tree._forest = self
            self.append(tree)

    def phrase_by_id(self, tree_id, id):
        try:
            tree = self[int(tree_id)]
        except IndexError:
            warnings.warn('TREE+INDEX out of forest range.')
            return None

        return tree.phrase_by_id(id)
