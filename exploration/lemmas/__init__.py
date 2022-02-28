from lemmas.farthest_recovery_publish import FarthestRecoveryPublish
from lemmas.lemma_g8 import LemmaG8
from lemmas.largest_publish import LargestPublish
from lemmas.non_checkpoint_finality import NonCheckpointFinality

lemmas = [
    FarthestRecoveryPublish(),
    LemmaG8(),
    LargestPublish(),
    NonCheckpointFinality(),
]