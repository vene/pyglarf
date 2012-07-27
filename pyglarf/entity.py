from collections import defaultdict
from itertools import product


# score counts the amount of semantic info, I hope
score = lambda np: -len(filter(lambda (key, val):
                          key == 'PATTERN' and val == 'NAME' or
                          key == 'SEM-FEATURE' or
                          key == 'NE-TYPE',
                          np.attrs.items()))


def entities(nps, unite='YES'):
    """Builds a dictionary of entity-attributes from a sequence of NPs"""
    nps = list(nps)
    nps_by_id = {}

    # disjoint sets data structure
    ##############################
    rep = range(0, len(nps))

    def find(p):
        if rep[p] != p:
            rep[p] = find(rep[p])
        return rep[p]

    def union(p, q):
        # q should be the one with more semantic info:
        p, q = (q, p) if score(nps[p][0]) > score(nps[q][0]) else (p, q)
        rep[find(p)] = find(q)

    if unite == 'YES':
        for ptr, (np, _) in enumerate(nps):
            nps_by_id[np.index] = ptr
        # solve apposites and similar links
        for _, ptr in nps_by_id.items():
            linked_structures = [nps_by_id.get(link_idx)
                                 for _, indices in nps[ptr][0].links.items()
                                 for link_idx in indices]

            linked_structures = filter(lambda x: x is not None, linked_structures)
            for linked_np in linked_structures:
                union(ptr, linked_np)

        # join entities with same head
        for p, q in product(xrange(len(nps)), xrange(len(nps))):
            try:
                if nps[p][0].head[0] == nps[q][1]:
                    union(p, q)
            except:
                pass

    groups = [[] for _ in xrange(len(nps))]
    for k in xrange(len(nps)):
        nps[k][0].entity = rep[k]
        groups[rep[k]].append(nps[k][0])
    groups = filter(len, groups)
    entities = defaultdict(lambda: ([], []))
    for group in groups:
        group = sorted(group, key=score)
        head_str = group[0].short_repr()
        entities[head_str][0].extend([np.short_repr() for np in group])
        entities[head_str][1].extend([
            val.print_flat(indices=False, structure=False)
            for np in group
            for val in np.subphrases.values()
        ])  # OR MAKE THEM DISTINCT??!

    return nps, entities
