from typing import List

from miner import Miner

class Block:

    def __init__(self, miner: Miner, created_at: int) -> None:
        """
        Create a block that was mined by `miner` at discrete timestamp `created_at`.
        """

        if not isinstance(miner, Miner):
            raise TypeError("Block.__init__: `miner` must be of type `Miner`")
        if not isinstance(created_at, int):
            raise TypeError("Block.__init__: `created_at` must be an `int`")
        if created_at < 0:
            raise ValueError(
                "Block.__init__: `created_at` must be nonnegative")
        if created_at == 0 and miner != Miner.GENESIS:
            raise ValueError("Block.__init__: only the GENESIS block may have `created_at = 0`")
        if miner == Miner.GENESIS and created_at != 0:
            raise ValueError("Block.__init__: the GENESIS block must have `created_at = 0`")

        self.miner: Miner = miner
        self.created_at: int = created_at

        self.is_published: bool = (miner == Miner.GENESIS)
        self.height: int = 0 if (miner == Miner.GENESIS) else -1
        self.parent: Block = None

    def publish(self, parent: 'Block') -> 'Block':
        """
        Publish `self` to point to `Block` object `parent` and return `self`.
        """

        if self.is_published:
            raise RuntimeError("Block.publish: can only publish a block once")
        if not isinstance(parent, Block):
            raise TypeError("Block.publish: `parent` must be of type `Block`")
        if not parent.is_published:
            raise ValueError(
                "Block.publish: `parent` must be an already published block")
        if parent.created_at >= self.created_at:
            raise ValueError(
                "Block.publish: `parent` must be created at an earlier time than this block")

        self.is_published = True
        self.height = parent.height + 1
        self.parent = parent

        return self

    def ancestors(self) -> List['Block']:
        """
        Return all ancestors of `self` as a list of `Block` objects.
        Note: A block is its own 0th ancestor.
        """
        ancestors = [self]
        ancestor = self.parent

        while ancestor is not None:
            ancestors.append(ancestor)
            ancestor = ancestor.parent

        return ancestors

    def __repr__(self) -> str:
        """
        Return a string representing the current block.
        """
        return f"|{self.created_at}{(' -> ' + str(self.parent.created_at)) if self.parent is not None else ''}|"

if __name__ == "__main__":

    blocks = [
        Block(Miner.GENESIS, 0),
        Block(Miner.ATTACKER, 1),
        Block(Miner.HONEST, 2),
        Block(Miner.ATTACKER, 3),
    ]

    print()
    print(blocks[1].publish(blocks[0]))
    print(blocks[2].publish(blocks[0]))
    print(blocks[3].publish(blocks[1]))
    print()

    print()
    print(blocks[2].ancestors())
    print(blocks[3].ancestors())
    print()
