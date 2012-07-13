# pyglarf

Python utilities for wrapping and working on top of
[GLARF](http://nlp.cs.nyu.edu/meyers/GLARF.html)'s output.

## Context

I have started developing this module while working on textual entailment and
needing to leverage GLARF's rich output. Realizing that the most difficult part
is actually reading the structures as GLARF meant them, I started factoring out
the useful parts into this package.

For this reason, the tasks this is useful for might be restricted to CPA-style
work at the moment, but I look forward to contributions, and will extend it
myself as well, wherever my projects will lead me.

## Installation

This module requires `nltk.Tree` for parsing TreeBank-style paranthesised
trees.

## Example

    >>> with GlarfWrapper() as gw:
    ...     _, _, glarf_out = gw.make_sentences("John died in Boston in 1972.")
    ... 
    >>> tree = GlarfTree.glarf_parse(glarf_out[0])
    >>> print list(tree.rels())
    [DIE/1 [CATEGORY: VG, INDEX: 10, SENSE-NAME: "STERBEN", VERB-SENSE: 1, PARENT_CATEGORY: VP]
    P-ARG1 [SBJ NP INDEX: 5]:  John/0
    P-ARGM-LOC [ADV2 PP INDEX: 12]:  in/4 |1972|/5
    ADV1 [PP INDEX: 11]: in/2 Boston/3
    ADV2 [PP INDEX: 12]: in/4 |1972|/5
    ]
    >>> tree.entities()
    {'9': ('|1972|', []), '8': ('Boston', []), '5': ('John', []), 'leaf5': ('|1972|', [])}

## Future plans

* Write documentation and tests
* Try to cover the entire GLARF specification (help appreciated!)

## License

Simplified BSD License, (C) 2012 Vlad Niculae.
