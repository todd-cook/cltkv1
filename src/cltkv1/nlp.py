"""Primary module for CLTK pipeline."""

import re
from collections import namedtuple
from typing import List

from cltkv1.tokenizers import TokenizeWord
from cltkv1.wrappers import StanfordNLPWrapper

# The idea behind this namedtuple is that one of these will be implemented for each token in the NLP object.
# It will be held in a list. From this,
# TODO: Fill out more attributes to this
fields_text = [
    "indices_sentences",
    "indices_tokens",
    "language",
    "tokens",
    "pipeline",
    "raw",
]
Text = namedtuple("Text", fields_text, defaults=(None,) * len(fields_text))
fields_word = [
    "index_char_start",
    "index_char_stop",
    "index_token",
    "index_sentence",
    "string",
    "pos",
    "scansion",
]
Word = namedtuple("Word", fields_word, defaults=(None,) * len(fields_word))


class NLP:
    """Primary class for NLP pipeline.

    >>> cltk_nlp = NLP(language='greek')
    >>> cltk_nlp.language
    'greek'
    >>> john_damascus_corinth = "Τοῦτο εἰπὼν, ᾐνίξατο αἰτίους ὄντας τοῦ τὰ ἐλάσσονα λαμβάνειν, καὶ κυρίους, εἰ βούλοιντο, τοῦ τὰ μείζονα. Ἔστι δὲ πολὺ μείζων ἡ ἀγάπη πάντων τῶν χαρισμάτων."
    >>> john_text_analyzed = cltk_nlp.analyze(john_damascus_corinth)
    >>> john_text_analyzed.language
    'greek'
    >>> john_text_analyzed.indices_sentences
    [[103, 104], [154, 155]]
    >>> john_text_analyzed.indices_tokens[0:3]
    [[0, 5], [6, 11], [13, 20]]
    >>> tokens = cltk_nlp.get_tokens(analyzed_text=john_text_analyzed)
    >>> tokens[0:3]
    ['Τοῦτο', 'εἰπὼν', 'ᾐνίξατο']
    """

    def __init__(self, language: str, pipeline: List[str] = None) -> None:
        """Constructor for CLTK class.

        >>> cltk_nlp = NLP(language='greek')
        >>> isinstance(cltk_nlp, NLP)
        True
        """
        self.language = language
        if not pipeline:
            # look up default pipeline for given language
            self.pipeline = pipeline
        else:
            # confirm that user-defined pipeline is possible
            self.pipeline = pipeline

    def analyze(self, text: str) -> Text:
        """The primary method for the NLP object, to which raw text strings are passed.

        >>> cltk_nlp = NLP(language='latin')
        >>> isinstance(cltk_nlp, NLP)
        True
        >>> galileo_sidereus = "Preclarum sane atque humanitatis plenum eorum fuit institutum, qui excellentium virtute virorum res preclare gestas ab invidia tutari, eorumque immortalitate digna nomina ab oblivione atque interitu vindicare, conati sunt. Hinc ad memoriam posteritatis prodite imagines, vel marmore insculpte, vel ex ere ficte; hinc posite statue, tam pedestres, quam equestres; hinc columnarum atque pyramidum, ut inquit ille, sumptus ad sidera ducti; hinc denique urbes edificate, eorumque insignite nominibus, quos grata posteritas eternitati commendandos existimavit. Eiusmodi est enim humane mentis conditio, ut nisi assiduis rerum simulacris in eam extrinsecus irrumpentibus pulsetur, omnis ex illa recordatio facile effluat."
        >>> analyzed_text = cltk_nlp.analyze(galileo_sidereus)
        >>> analyzed_text.language
        'latin'
        >>> analyzed_text.indices_sentences
        [[221, 222], [554, 555], [714, 715]]
        >>> analyzed_text.indices_tokens[0:3]
        [[0, 9], [10, 14], [15, 20]]
        """
        # Get the stops/start char indices of where sentences begin and end
        indices_sentences = list()
        pattern_sentence = re.compile(r"\.")
        for sentence_match in pattern_sentence.finditer(string=text):
            idx_sentence_start, idx_sentence_stop = sentence_match.span()
            indices_sentences.append([idx_sentence_start, idx_sentence_stop])

        # Get the start/stop char indices of word boundaries
        indices_words = list()
        pattern_word = re.compile(r"\w+")
        for word_match in pattern_word.finditer(string=text):
            idx_word_start, idx_word_stop = word_match.span()
            indices_words.append([idx_word_start, idx_word_stop])

        # Populate the main object returned by this class
        text = Text(
            indices_sentences=indices_sentences,
            indices_tokens=indices_words,
            language=self.language,
            raw=text,
        )
        return text

    def get_tokens(self, analyzed_text: Text):
        """Using the pre-processed Text object, return list of token strings.

        >>> cltk_nlp = NLP(language='latin')
        >>> galileo_sidereus = "Preclarum sane atque humanitatis plenum eorum fuit institutum, qui excellentium virtute virorum res preclare gestas ab invidia tutari, eorumque immortalitate digna nomina ab oblivione atque interitu vindicare, conati sunt. Hinc ad memoriam posteritatis prodite imagines, vel marmore insculpte, vel ex ere ficte; hinc posite statue, tam pedestres, quam equestres; hinc columnarum atque pyramidum, ut inquit ille, sumptus ad sidera ducti; hinc denique urbes edificate, eorumque insignite nominibus, quos grata posteritas eternitati commendandos existimavit. Eiusmodi est enim humane mentis conditio, ut nisi assiduis rerum simulacris in eam extrinsecus irrumpentibus pulsetur, omnis ex illa recordatio facile effluat."
        >>> analyzed_text = cltk_nlp.analyze(galileo_sidereus)
        >>> tokens = cltk_nlp.get_tokens(analyzed_text=analyzed_text)
        >>> tokens[0:3]
        ['Preclarum', 'sane', 'atque']
        """
        tokens = list()
        indices_tokens = analyzed_text.indices_tokens
        for indices in indices_tokens:
            start, end = indices[0], indices[1]
            token = analyzed_text.raw[start:end]
            tokens.append(token)
        return tokens
