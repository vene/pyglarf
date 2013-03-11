"""Driver for Glarf: runs in a temporary folder and captures the output.

Requires Glarf, sbcl, perl but takes care of the environment variables, as long
as sbcl and perl are where they should.

"""

# Author: Vlad Niculae <vlad@vene.ro>
# License: BSD

import os
import re
import shutil
import tempfile

from subprocess import call

PATH = '/Users/vene/fbk/kits/glarf'


def _split_glarf_tuples(txt_tuples):
    """Splits raw tuple file into array of arrays, handling missing trees"""
    tp_dict = {}
    for tree_tuples in txt_tuples.split(';;')[1:]:
        tuple_lines = tree_tuples.splitlines()
        # First line looks like "Tuples for Tree 152"
        tree_idx = int(tuple_lines[0].rsplit(' ', 1)[1])
        tuples = tuple_lines[1:]
        tp_dict[tree_idx] = tuples
    # Build array from int-keyed dict, filling missing values with None
    return [tp_dict.get(k, None) for k in xrange(max(tp_dict.keys()) + 1)]


class GlarfWrapper(object):
    """Wrapper object for convenient invocation of Glarf from Python.

    All the operations happen through the filesystem.

    Parameters
    ----------
    path, string:
        the root of the local Glarf installation
    verbose, int:
        verbosity degree.
        1: displays the log file on object creation
        2: in addition, prints glarf commands being run

    Examples
    --------
    >>> para = "A man arrived. He was whistling."
    >>> with GlarfWrapper() as glarf:
    ...     sent_out, parse_out, glarf_out, tuple_out = glarf.make_paragraphs(para)
    >>> for s, p, g, t in zip(sent_out, parse_out, glarf_out, tuple_out):
    ...     print s
    ...     print p
    ...     print g
    ...     print t
    0 A man arrived.
    (S1 (S (NP (DT A) (NN man)) (VP (VBD arrived)) (. .)))
    ((S
      (SBJ (NP (Q-POS (DT A 0)) (HEAD (NN man 1)) (PTB2-POINTER |0+1|) (INDEX 2)))
      (PRD
       (VP
        (HEAD
         (VG (HEAD (VBD arrived 2)) (P-ARG1 (NP (EC-TYPE PB) (INDEX 2))) (INDEX 3)
          (BASE ARRIVE) (VERB-SENSE 1) (SENSE-NAME "MOVE, COME TO")))
        (PTB2-POINTER |2+1|)))
      (PUNCTUATION (|.| |.| 3)) (PTB2-POINTER |0+2|) (TREE-NUM 0) (FILE-NAME "tmp")
      (INDEX 0) (SENTENCE-OFFSET 0)))
    ['SBJ | SBJ | ARG1 | NIL | NIL | arrived | 6 | 2 | VBD | ARRIVE | NIL | NIL | NIL | 1 | NIL | NIL | NIL | man | 2 | 1 | NN | MAN | NIL | NIL | NIL ', 'Q-POS | Q-POS | NIL | NIL | NIL | man | 2 | 1 | NN | MAN | NIL | NIL | NIL | NIL | NIL | NIL | NIL | A | 0 | 0 | DT | A | NIL | NIL | NIL ']
    15 He was whistling.
    (S1 (S (NP (PRP He)) (VP (AUX was) (VP (VBG whistling))) (. .)))
    ((S (SBJ (NP (HEAD (PRP He 0)) (PTB2-POINTER |0+1|) (INDEX 2)))
      (PRD
       (VP
        (HEAD
         (VG (AUX (VBD was 1)) (HEAD (VBG whistling 2))
          (P-ARG0 (NP (EC-TYPE PB) (INDEX 2))) (INDEX 3) (BASE WHISTLE)
          (VERB-SENSE 1) (SENSE-NAME "MAKE A   WHISTLING NOISE")))
        (PTB2-POINTER |1+1|)))
      (PUNCTUATION (|.| |.| 3)) (PTB2-POINTER |0+2|) (TREE-NUM 1) (FILE-NAME "tmp")
      (INDEX 0) (SENTENCE-OFFSET 15)))
    ['SBJ | SBJ | ARG0 | NIL | NIL | whistling | 22 | 2 | VBG | WHISTLE | NIL | NIL | NIL | 1 | NIL | NIL | NIL | He | 15 | 0 | PRP | HE | NIL | NIL | NIL ', 'AUX | AUX | NIL | NIL | NIL | whistling | 22 | 2 | VBG | WHISTLE | NIL | NIL | NIL | 1 | NIL | NIL | NIL | was | 18 | 1 | VBD | BE | NIL | NIL | NIL ']

    TODO: if it's too slow, support batch
    """
    def __init__(self, path=PATH, verbose=0):
        self.path = path
        self.verbose = verbose
        self._glarf_regex = re.compile('(\(\(\*\*\*ERROR\*\*\*\)\)|'
                                       '\(\(.*?\(SENTENCE-OFFSET [0-9]+\)+)',
                                       re.DOTALL)

    def __enter__(self):
        self.wd = tempfile.mkdtemp()
        self.log = tempfile.mkstemp()
        if self.verbose >= 1:
            print self.log[1]
        # set environment variables
        os.environ['GLARF'] = self.path
        os.environ['GLARF_JET'] = os.path.join(self.path, 'JET')
        os.environ['PATH'] += ':.'
        successful_copy = call(['copy-glarf-scripts ' + self.wd], shell=True,
                               cwd=os.path.join(self.path, 'commands-2010'))
        assert successful_copy == 0

        os.mkdir(os.path.join(self.wd, 'tmp'))
        in_file = os.path.join(self.wd, 'tmp', 'tmp.sgm')
        self._filenames = {
            'in': in_file,
            'jet': in_file + '.sent',
            'parse': in_file + '.sent.chout',
            'glarf': in_file + '.sent.ns-autopb101e',
            'tuple': in_file + '.sent.ns-2005-fast-ace-n-tuple101e'
        }
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.wd)  # delete directory

    def _invoke_glarf(self, type, args):
        """Invokes $ make-all-glarf-type target_dir args"""

        cmd = 'make-all-glarf-%s tmp %s' % (type, args)
        if self.verbose >= 2:
            print cmd

        successful_call = call(cmd, cwd=self.wd, shell=True,
                               stderr=self.log[0], stdout=self.log[0])
        # FIXME: returns 0 even when it fails!!
        if successful_call != 0:
            raise RuntimeError('Glarf invocation failed. Output log can be '
                               'found in %s.' % self.log[1])

        return tuple(open(self._filenames[k]).read()
                     for k in ('jet', 'parse', 'glarf', 'tuple'))

    def make_sentences(self, sentences):
        """Parse and analyze a sequence of sentences.

        Invokes `make-all-glarf-a (...) N`.

        Parameters
        ----------
        sentences, iterateble or string:
            The sequence of sentences (strings) that Glarf will process.

        Returns
        -------
        jet_output: list, length: len(sentences)
            The list of input sentences, prefixed with offset numbers.
            Corresponds to the file extension .sgm.sent from the Glarf output.

        parse_output: list, length: len(sentences)
            The list of parse trees obtained from the input sentences.
            Corresponds to the file extension .sgm.chout from the Glarf output.

        glarf_output: list, length: len(sentences)
            The list of Glarf trees obtained from the input sentences.
            Corresponds to the file extension .sgm.ne-auto(...) from the Glarf
            output.

        tuple_output: list, length: len(sentences)
            The list of tuples obtained from the input sentences.
            Corresponds to the file extension .sgm.ns-2005-fast-ace-n-tuple101e
            from the Glarf output.  Some of the information in the tuples, such
            as noun lemmas, is not present in the .sgm.ne-autopb101e file.
        """
        if isinstance(sentences, str):
            sentences = [sentences]

        with open(self._filenames['in'], 'w') as infile:
            infile.writelines('<sentence>%s</sentence>\n' % sent
                              for sent in sentences)

        jet_out, parse_out, glarf_out, tuple_out = self._invoke_glarf('a', 'N')
        return (jet_out.splitlines(),
                filter(lambda x: not x.startswith('#') and len(x) > 0,
                       (s.strip() for s in parse_out.splitlines())),
                filter(len, (s.strip() for s
                             in re.split(self._glarf_regex, glarf_out))),
                _split_glarf_tuples(tuple_out))

    def make_paragraphs(self, paragraphs):
        """Parse and analyze a sequence of paragraphs.

        Invokes `make-all-glarf-b (...) N P`.

        Parameters
        ----------
        sentences, iterateble or string:
            The sequence of sentences (strings) that Glarf will process.

        Returns
        -------
        jet_output: list, length: len(sentences)
            The list of input sentences, prefixed with offset numbers.
            Corresponds to the file extension .sgm.sent from the Glarf output.

        parse_output: list, length: len(sentences)
            The list of parse trees obtained from the input sentences.
            Corresponds to the file extension .sgm.chout from the Glarf output.

        glarf_output: list, length: len(sentences)
            The list of Glarf trees obtained from the input sentences.
            Corresponds to the file extension .sgm.ne-auto(...) from the Glarf
            output.

        tuple_output: list, length: len(sentences)
            The list of tuples obtained from the input sentences.
            Corresponds to the file extension .sgm.ns-2005-fast-ace-n-tuple101e
            from the Glarf output.  Some of the information in the tuples, such
            as noun lemmas, is not present in the .sgm.ne-autopb101e file.

        """
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]

        with open(self._filenames['in'], 'w') as infile:
            infile.writelines(['<TEXT><P>%s</P></TEXT>\n' % par
                              for par in paragraphs])

        jet_out, parse_out, glarf_out, tuple_out = self._invoke_glarf('b',
                                                                      'N P')
        return (jet_out.splitlines(),
                filter(lambda x: not x.startswith('#') and len(x) > 0,
                       (s.strip() for s in parse_out.splitlines())),
                [s.strip() for s in re.findall(self._glarf_regex, glarf_out)],
                _split_glarf_tuples(tuple_out))
