# -------------------------------------------------------------------------------
# A class for modeling a block in the proof-of-stake mining game with
# external randomness proposed by Ferreira and Weinberg.
#
# @author Anthony Hein
# @version 1.0
# -------------------------------------------------------------------------------

from typing import List


class Block:
    def __init__(self, miner_idx: int, created_at: int) -> None:

        self.miner_idx: int = miner_idx
        self.created_at: int = created_at

        self.is_published: bool = False
        self.height: int = None
        self.parent: Block = None
        self.children: List[Block] = []

    def publish(self, parent: 'Block') -> 'Block':

        assert (
            not parent or parent.is_published
        ), "Publishing a block with an edge to an unpublished block."
        assert (
            not parent or (parent.created_at < self.created_at)
        ), f"Publishing a block with an edge to a newer block: {parent} {parent.created_at} {self.created_at}"
        assert not self.is_published, "Publishing the same block more than once."

        self.is_published = True
        self.parent = parent

        if self.parent:
            self.height = self.parent.height + 1
            self.parent.children.append(self)

        else:
            self.height = 0

        return self

    def ancestors(self) -> List['Block']:

        ancestors = [self]
        parent = self.parent

        while parent:
            ancestors.append(parent)
            parent = parent.parent

        return ancestors

    def kth_ancestor(self, k) -> 'Block':

        ancestor = self

        kp = k

        while kp > 0:

            assert ancestor.parent, f"Block does not have requested number of ancestors: {self.ancestors()} {k}"

            ancestor = ancestor.parent
            kp -= 1

        return ancestor

    def get_miner_idx(self) -> int:
        return self.miner_idx

    def get_height(self) -> int:
        return self.height

    def get_created_at(self) -> int:
        return self.created_at
