from typing import List

from lemmas.lemma import Lemma
from lemmas.lemma_g8 import LemmaG8
from lemmas.non_checkpoint_finality import NonCheckpointFinality

lemmas: List[Lemma] = [
    LemmaG8(),
    NonCheckpointFinality(),
]