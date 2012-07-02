# pyglarf

Python utilities for working on top of
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

TODO

## Future plans

* Wrap GLARF completely, so it's easier to test this out for a few sentences.
* Write documentation and tests
* Try to cover the entire GLARF specification (help appreciated!)

## License

Simplified BSD License, (C) 2012 Vlad Niculae.
