"""Driver for GLARF: runs in a temporary folder and captures the output.

Requires GLARF and sbcl but takes care of the environment
variables, as long as sbcl and perl are where they should.

"""

import os
import re
import shutil
import tempfile
from StringIO import StringIO

from subprocess import call

PATH = '/Users/vene/fbk/kits/glarf'


class Glarf(object):
    """Wrapper object for convenient invocation of Glarf from Python.

    Example:
        >>> para = "A man arrived. He was whistling."
        >>> with Glarf() as glarf:
        ...     sent_out, parse_out, glarf_out = glarf.make_paragraphs(para)
        >>> for s, p, g in zip(sent_out, parse_out, glarf_out):
        ...     print s
        ...     print p
        ...     print g
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

    TODO: if it's too slow, support batch
    """
    def __init__(self, path=PATH):
        self.path = path
        self._glarf_regex = re.compile('(\(\(.*?\(SENTENCE-OFFSET [0-9]+\)+)',
                                       re.DOTALL)

    def __enter__(self):
        self.wd = tempfile.mkdtemp()
        self.log = tempfile.mkstemp()
        # set environment variables
        os.environ['GLARF'] = PATH
        os.environ['GLARF_JET'] = os.path.join(PATH, 'JET')
        os.environ['PATH'] += ':.'
        successful_copy = call(['copy-glarf-scripts ' + self.wd], shell=True,
                               cwd=os.path.join(PATH, 'commands-2010'))
        assert successful_copy == 0

        os.mkdir(os.path.join(self.wd, 'tmp'))
        in_file = os.path.join(self.wd, 'tmp', 'tmp.sgm')
        self._filenames = {
            'in': in_file,
            'jet_out': in_file + '.sent',
            'parse_out': in_file + '.sent.chout',
            'glarf_out': in_file + '.sent.ns-autopb101e'
        }
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.wd)  # delete directory

    def _invoke_glarf(self, type, args):
        """Invokes $ make-all-glarf-type target_dir args"""
        successful_call = call(['make-all-glarf-%s tmp %s' % (type, args)],
                               cwd=self.wd, shell=True, stderr=self.log[0],
                               stdout=self.log[0])
        # FIXME: returns 0 even when it fails!!
        if successful_call != 0:
            raise RuntimeError('Glarf invocation failed. Output log can be '
                               'found in %s.' % self.log[1])

        jet_output = open(self._filenames['jet_out']).read()
        parse_output = open(self._filenames['parse_out']).read()
        glarf_output = open(self._filenames['glarf_out']).read()

        return jet_output, parse_output, glarf_output

    def make_sentences(self, sentences):
        if isinstance(sentences, str):
            sentences = [sentences]

        with open(self._filenames['in'], 'w') as infile:
            infile.writelines('<sentence>%s</sentence>\n' % sent
                              for sent in sentences)

        jet_output, parse_output, glarf_output = self._invoke_glarf('a', 'N')
        return (jet_output.splitlines(),
                filter(lambda x: not x.startswith('#') and len(x) > 0,
                       (s.strip() for s in parse_output.splitlines())),
                filter(len, (s.strip() for s
                             in re.split(self._glarf_regex, glarf_output))))

    def make_paragraphs(self, paragraphs):
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]

        with open(self._filenames['in'], 'w') as infile:
            infile.writelines('<TEXT><P>%s</P></TEXT>\n' % par
                              for par in paragraphs)

        jet_output, parse_output, glarf_output = self._invoke_glarf('b', 'N P')
        return (jet_output.splitlines(),
                filter(lambda x: not x.startswith('#') and len(x) > 0,
                       (s.strip() for s in parse_output.splitlines())),
                filter(len, (s.strip() for s
                             in re.split(self._glarf_regex, glarf_output))))
