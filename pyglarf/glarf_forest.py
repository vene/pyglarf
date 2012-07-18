from pyglarf import GlarfTree


class GlarfForest(list):
    """A forest of GlarfTrees

    GlarfForest implements a frendlier interface than building GlarfTrees
    individually.

    Parameters
    ----------

    glarf_parses: list of strings,
        List of Glarf output strings with which to build the forest. This
        is the third return value of GlarfWrapper.make_* functions.
    """

    def __init__(self, glarf_parses):
        self.extend(GlarfTree.glarf_parse(s) for s in glarf_parses)

    def phrase_by_id(self, tree, id):
        return self[tree].phrase_by_id(id)
