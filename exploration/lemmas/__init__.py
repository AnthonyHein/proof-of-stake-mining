from lemmas.checkpoint_recurrence import CheckpointRecurrence
from lemmas.farthest_recovery_publish import FarthestRecoveryPublish
from lemmas.largest_publish import LargestPublish
from lemmas.lemma_g8 import LemmaG8
from lemmas.non_checkpoint_finality import NonCheckpointFinality

lemmas = [
    CheckpointRecurrence(),
    FarthestRecoveryPublish(),
    LargestPublish(),
    LemmaG8(),
    NonCheckpointFinality(),
]