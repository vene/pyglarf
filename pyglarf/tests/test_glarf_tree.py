from pyglarf import GlarfTree

# A slightly modified tree from ns-autopb101e
# where I added a random unmatched paranthesis in
# the SENSE-NAME. This sometimes occurs in real data.

test_sentence = """\
((S
  (ADV
   (PP (HEAD (IN In 0))
    (OBJ
     (NP
      (HEAD
       (NP (HEAD (CD |2003| 1)) (REG-NUMBER 2003) (PATTERN NUMBERP)
        (TRANSPARENT T) (SEM-FEATURE NUMBER)))
      (PTB2-POINTER |1+1|) (SEM-FEATURE TMP) (PATTERN DATE) (NE-TYPE YEAR)
      (REG-DATE "2003") (INDEX 14)))
    (PTB2-POINTER |0+1|) (FOCUS T) (INDEX 17)))
  (PUNCTUATION1 (|,| |,| 2))
  (SBJ
   (NP (HEAD (NNP Yahoo 3)) (SEM-FEATURE COMMUNICATOR) (NE-TYPE ORGANIZATION)
    (PUNCTUATION (|.| ! 4)) (PTB2-POINTER |3+1|) (INDEX 10)))
  (PRD
   (VP
    (HEAD
     (VG (HEAD (VBD acquired 5)) (P-ARGM-LOC (PP (EC-TYPE PB) (INDEX 17)))
      (P-ARG3 (PP (EC-TYPE PB) (INDEX 19)))
      (P-ARG1 (NP (EC-TYPE PB) (INDEX 15)))
      (P-ARG0 (NP (EC-TYPE PB) (INDEX 10))) (INDEX 18) (BASE ACQUIRE)
      (VERB-SENSE 1) (SENSE-NAME "GET, (ACQUIRE")))
    (OBJ
     (NP (NAME (NNP Overture 6)) (PTB2-POINTER |6+1|)
      (SEM-FEATURE COMMUNICATOR) (NE-TYPE ORGANIZATION) (PATTERN NAME)
      (INDEX 15)))
    (COMP
     (PP (HEAD (IN for 7))
      (OBJ
       (NP
        (Q-POS
         (QP (S-UNIT (NP (HEAD ($ $ 8)) (INDEX 1)))
          (HEAD
           (NP (NUMBER1 (CD |1.63| 9)) (NUMBER2 (CD billion 10))
            (PATTERN NUMBERP) (TRANSPARENT T) (SEM-FEATURE NUMBER)
            (REG-NUMBER 1.63e9)))
          (TRANSPARENT T)))
        (L-HEAD (NP (EC-TYPE UNIT) (INDEX 1))) (PTB2-POINTER |8+1|)
        (SEM-FEATURE NUMBER) (INDEX 16)))
      (PTB2-POINTER |7+1|) (INDEX 19)))
    (PTB2-POINTER |5+1|)))
  (PUNCTUATION2 (|.| |.| 11)) (PTB2-POINTER |0+2|) (TREE-NUM 0)
  (FILE-NAME "dummy") (INDEX 0) (SENTENCE-OFFSET 0)))

"""


def test_successful_parse():
    GlarfTree.glarf_parse(test_sentence)
