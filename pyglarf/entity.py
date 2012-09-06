from collections import defaultdict
from itertools import product


# score counts the amount of semantic info, I hope
score = lambda np: -len(filter(lambda (key, val):
                          key == 'PATTERN' and val == 'NAME' or
                          key == 'SEM-FEATURE' or
                          key == 'NE-TYPE',
                          np.attrs.items()))


def x_is_alpha(rels, include_aux=True, alpha_head=False):
    # Try to return a semantic interpretation of the hypothesis, else None
    for rel in rels:
        if rel.head == 'BE':
            try:
                x = rel.args['P-ARG1'][3][0]
                if len(rel.args['P-ARG1'][3]) > 1:
                    for k in rel.args['P-ARG1'][3]:
                        print k
                alpha = rel.args['P-ARG2'][3][0]
                if alpha_head:
                    head = alpha[0].head()
                    if head:
                        # skip through transparent links UGLY :(
                        deep = head[0].head()
                        if deep and 'TRANSPARENT' in deep[0].daughters():
                            comps = [subtr for subtr in alpha[0]
                                     if subtr.node == 'COMP']
                            if comps:
                                alpha = comps[0]
                                head = alpha[0].head()
                        # skip through prepositions
                        if head[0].node == 'IN':
                            objs = [subtr for subtr in alpha[0]
                                     if subtr.node == 'OBJ']
                            if objs:
                                alpha = objs[0]
                                alpha = alpha.head() if alpha.head() else alpha
                            #print alpha
                        else:
                            alpha = head
                    #alpha = alpha.most_specific_head()
                yield x, alpha
            except KeyError:
                pass
        if include_aux and any('is' in aux.leaves()
                               for aux in rel.aux.values()):
            pass


def entities(nps, rels=None, unite='YES'):
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
    counter = 0
    if unite == 'YES':
        for ptr, (np, _) in enumerate(nps):
            nps_by_id[np.index] = ptr

        # join entities with same head
        for p, q in product(xrange(len(nps)), xrange(len(nps))):
            try:
                if nps[p][0].head[0] == nps[q][1]:
                    union(p, q)
            except:
                pass
            # or if they are tied by a relation
            for r in rels:
                arg_ids = [i for _, _, ids, _ in r.args.values() for i in ids]

                if nps[p][0].index in arg_ids and nps[q][0].index in arg_ids:
                    union(p, q)

        # solve apposites and similar links
        for _, ptr in nps_by_id.items():
            linked_structures = [nps_by_id.get(link_idx)
                                 for _, indices in nps[ptr][0].links.items()
                                 for link_idx in indices]

            linked_structures = filter(lambda x: x is not None, linked_structures)
            for linked_np in linked_structures:
                union(ptr, linked_np)

        # join entities with same head again
        # crazy but works good. algorithmic trick needed here!!!
        for p, q in product(xrange(len(nps)), xrange(len(nps))):
            try:
                if nps[p][0].head[0] == nps[q][1]:
                    union(p, q)
            except:
                pass
            # or if they are tied by a relation
            for r in rels:
                arg_ids = [i for _, _, ids, _ in r.args.values() for i in ids]

                if nps[p][0].index in arg_ids and nps[q][0].index in arg_ids:
                    union(p, q)

    groups = [[] for _ in xrange(len(nps))]
    for ptr, (np, _) in zip(rep, nps):
        np.entity = ptr
        groups[np.entity].append(np)

    #groups = filter(len, groups)
    entities = defaultdict(lambda: ([], []))
    for group in groups:
        if not len(group):
            continue
        group = sorted(group, key=score)
        head_str = group[0].short_repr()
        for np in group:
            if not np.conj:
                entities[head_str][0].append(np.short_repr())
                entities[head_str][1].extend(val.print_flat(indices=False,
                                             structure=False, skip_det=True)
                                             for val in np.subphrases.values()
                                             if val.node != 'DT')
                #entities[head_str][1].extend(val.print_flat(indices=False,
                #                             structure=False, skip_det=True)
                #                             for phr in np.subphrases.values()
                ##                             for val in phr
                #                             if not isinstance(val, str))
    #

    #add X is alphas

    for x, alpha in x_is_alpha(rels, False, True):
        try:
            ptr = find(nps.index(x.nps().next()))
            entities[groups[ptr][0].short_repr()][1].append(alpha.print_flat(False, False, True))
        except:
            pass

    return nps, entities
