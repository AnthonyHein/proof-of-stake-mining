from typing import List

from block import Block
from block_utils import *
from miner import Miner


class Tree:

    def __init__(self) -> None:
        """
        Create an empty block tree.
        """

        self.genesis: Block = Block(Miner.GENESIS, 0)
        self.blocks: List[Block] = [self.genesis]
        self.longest_chain: Block = self.genesis

    def _get_longest_chain(self) -> Block:
        """
        Get the longest chain among the blocks in this tree.
        """
        height_of_longest_chain = max([block.height for block in self.blocks])

        longest_chain: Block = None
        for block in self.blocks:
            if block.height == height_of_longest_chain:
                if longest_chain is None or block.created_at < longest_chain.created_at:
                    longest_chain = block

        return longest_chain

    def capitulate(self, genesis: Block) -> 'Tree':
        """
        Modify the tree so that the block `genesis` is effectively the genesis block.
        """

        if not isinstance(genesis, Block):
            raise TypeError("Tree.capitulate: `genesis` must be of type `Block`")
        if genesis not in self.blocks:
            raise ValueError("Tree.capiulate: `genesis` must be an existing block in the tree")

        blocks = [
            block
            for block
            in self.blocks
            if block.created_at >= genesis.created_at and \
               (not block.is_published or genesis in block.ancestors())
        ]

        genesis_prev_height = genesis.height
        genesis_prev_created_at = genesis.created_at

        for block in blocks:
            if block == genesis:
                block = relabel_block(block, genesis_prev_height, genesis_prev_created_at, True)
            else:
                block = relabel_block(block, genesis_prev_height, genesis_prev_created_at, False)

        self.blocks = blocks
        self.longest_chain = self._get_longest_chain()

        return self

    def publish_set(self, miner: Miner, blocks: List[Block], edges: dict[Block, Block]) -> 'Tree':
        """
        Publish `blocks` mined by `miner` to this tree with edges defined by `edges` and return
        the resulting tree.
        """

        if not isinstance(blocks, list):
            raise TypeError(
                "Tree.publish_set: `blocks` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in blocks):
            raise TypeError(
                "Tree.publish_set: `blocks` must be of type `List[Block]`")
        if not isinstance(edges, dict):
            raise TypeError(
                "Tree.publish_set: `edges` must be of type `dict[Block, Block]`")
        if not all(isinstance(block_from, Block) and isinstance(block_to, Block) for block_from, block_to in edges.items()):
            raise TypeError(
                "Tree.publish_set: `edges` must be of type `dict[Block, Block]`")

        for block in blocks:
            if block.miner != miner:
                raise ValueError(
                    "Tree.publish_set: `miner` does not own the blocks in `blocks`")
            if block.is_published:
                raise ValueError(
                    "Tree.publish_set: the blocks in `blocks` must not already be published")
            if block not in edges.keys():
                raise ValueError(
                    "Tree.publish_set: all blocks in `blocks` must have an outgoing edge in `edges`")

        for edge_from, edge_to in edges.items():
            if not edge_from in blocks:
                raise ValueError(
                    "Tree.publish_set: all edges in `edges` must come from a block in `blocks`")
            if not (edge_to in blocks or edge_to in self.blocks):
                raise ValueError(
                    "Tree.publish_set: all edges in `edges` must go to a block in `blocks` or a block already in the tree")
            if edge_from.created_at <= edge_to.created_at:
                raise ValueError(
                    "Tree.publish_set: all edges in `edges` must point to a block that was created earlier")

        blocks = sort_blocks(blocks, reverse=False)

        for block in blocks:
            self.blocks.append(block.publish(edges[block]))

        self.longest_chain = self._get_longest_chain()

        return self

    def publish_path(self, miner: Miner, blocks: List[Block], anchor: Block) -> 'Tree':
        """
        Publish `blocks` mined by `miner` to this tree with an edge from the block of minimum
        `created_at` value to `anchor` and for every other block in `blocks` an edge to the
        largest block in `blocks` with a `created_at` value strictly less than it.
        """

        if not isinstance(blocks, list):
            raise TypeError(
                "Tree.publish_path: `blocks` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in blocks):
            raise TypeError(
                "Tree.publish_path: `blocks` must be of type `List[Block]`")
        if not isinstance(anchor, Block):
            raise TypeError(
                "Tree.publish_path: `anchor` must be of type `Block`")

        for block in blocks:
            if block.miner != miner:
                raise ValueError(
                    "Tree.publish_path: `miner` does not own the blocks in `blocks`")
            if block.is_published:
                raise ValueError(
                    "Tree.publish_path: the blocks in `blocks` must not already be published")
            if block.created_at < anchor.created_at:
                raise ValueError(
                    "Tree.publish_path: all blocks in `blocks` be created at a later time than `anchor`")

        if not anchor.is_published or anchor not in self.blocks:
            raise ValueError("Tree.publish_path: `anchor` must have already been published")

        blocks = sort_blocks(blocks, reverse=False)

        for i, block in enumerate(blocks):
            self.blocks.append(blocks[i].publish(anchor if i == 0 else blocks[i-1]))

        self.longest_chain = self._get_longest_chain()

        return self
    
    def publish(self, miner: Miner, blocks: List[Block], num_blocks: int, anchor: Block) -> 'Tree':
        """
        Publish the smallest `num_blocks` of the unpublished blocks `blocks` mined by miner
        `miner` to this tree with an edge from the block of minimum `created_at` value within
        the set of blocks that will be published on this turn to `anchor` and for every other
        block that will be published on this turn an edge to the largest block with a `created_at`
        value strictly less than it among those blocks that will be published on this turn.
        """
        if not isinstance(blocks, list):
            raise TypeError(
                "Tree.publish: `blocks` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in blocks):
            raise TypeError(
                "Tree.publish: `blocks` must be of type `List[Block]`")
        if not isinstance(num_blocks, int):
            raise TypeError(
                "Tree.publish: `num_blocks` must be of type `int`")
        if not isinstance(anchor, Block):
            raise TypeError(
                "Tree.publish: `anchor` must be of type `Block`")

        for block in blocks:
            if block.miner != miner:
                raise ValueError(
                    "Tree.publish: `miner` does not own the blocks in `blocks`")
            if block.is_published:
                raise ValueError(
                    "Tree.publish: the blocks in `blocks` must not already be published")
            if block.created_at < anchor.created_at:
                raise ValueError(
                    "Tree.publish: all blocks in `blocks` be created at a later time than `anchor`")
        
        if num_blocks > len(blocks):
            raise ValueError("Tree.publish: cannot publish more blocks than the number of unpublished blocks")

        if not anchor.is_published or anchor not in self.blocks:
            raise ValueError("Tree.publish: `anchor` must have already been published")

        blocks = sort_blocks(blocks, reverse=False)[:num_blocks]

        for i, block in enumerate(blocks):
            self.blocks.append(blocks[i].publish(anchor if i == 0 else blocks[i-1]))
            
        self.longest_chain = self._get_longest_chain()

        return self

    def __repr__(self) -> str:
        """
        Return a string representing the current tree.
        """
        s: str = ""

        height_of_longest_chain = max([block.height for block in self.blocks])

        longest_chain: Block = None
        for block in self.blocks:
            if block.height == height_of_longest_chain:
                if longest_chain is None or block.created_at < longest_chain.created_at:
                    longest_chain = block

        longest_path: List[Block] = sort_blocks(longest_chain.ancestors())

        s += "Longest path: "
        s += str(longest_path)
        s += "\n"

        forks = sort_blocks(
            [block for block in self.blocks if block not in longest_path])

        s += "Blocks not in the longest path: "
        s += str(forks)

        return s


if __name__ == "__main__":

    print("-------------------------------------------------------")
    print("Use `publish_set`")
    print("-------------------------------------------------------")

    tree = Tree()

    print()
    print(tree)
    print()

    blocks = [
        tree.genesis,
        Block(Miner.ATTACKER, 1),
        Block(Miner.HONEST, 2),
        Block(Miner.ATTACKER, 3),
    ]


    print()
    print(
        tree.publish_set(
            miner=Miner.HONEST,
            blocks=[blocks[2]],
            edges={blocks[2]: blocks[0]}
        )
    )
    print()

    print()
    print(
        tree.publish_set(
            miner=Miner.ATTACKER,
            blocks=[blocks[1], blocks[3]],
            edges={blocks[1]: blocks[0], blocks[3]: blocks[1]}
        )
    )
    print()

    print("-------------------------------------------------------")
    print("Use `publish_path`")
    print("-------------------------------------------------------")
    

    tree = Tree()

    print()
    print(tree)
    print()

    blocks = [
        tree.genesis,
        Block(Miner.ATTACKER, 1),
        Block(Miner.HONEST, 2),
        Block(Miner.ATTACKER, 3),
    ]


    print()
    print(
        tree.publish_path(
            miner=Miner.HONEST,
            blocks=[blocks[2]],
            anchor=blocks[0]
        )
    )
    print()

    print()
    print(
        tree.publish_path(
            miner=Miner.ATTACKER,
            blocks=[blocks[1], blocks[3]],
            anchor=blocks[0]
        )
    )
    print()

    print("-------------------------------------------------------")
    print("Use `publish`")
    print("-------------------------------------------------------")
    

    tree = Tree()

    print()
    print(tree)
    print()

    blocks = [
        tree.genesis,
        Block(Miner.ATTACKER, 1),
        Block(Miner.HONEST, 2),
        Block(Miner.ATTACKER, 3),
        Block(Miner.HONEST, 4),
        Block(Miner.ATTACKER, 5),
    ]


    print()
    print(
        tree.publish(
            miner=Miner.HONEST,
            blocks=[blocks[2], blocks[4]],
            num_blocks=1,
            anchor=blocks[0]
        )
    )
    print()

    print()
    print(
        tree.publish(
            miner=Miner.ATTACKER,
            blocks=[blocks[1], blocks[3], blocks[5]],
            num_blocks=2,
            anchor=blocks[0]
        )
    )
    print()


    print("-------------------------------------------------------")
    print("`capitulate`")
    print("-------------------------------------------------------")

    tree = Tree()

    print()
    print(tree)
    print()

    blocks = [
        tree.genesis,
        Block(Miner.ATTACKER, 1),
        Block(Miner.HONEST, 2),
        Block(Miner.ATTACKER, 3),
        Block(Miner.HONEST, 4),
    ]


    print()
    print(
        tree.publish_set(
            miner=Miner.HONEST,
            blocks=[blocks[2]],
            edges={blocks[2]: blocks[0]}
        )
    )
    print()

    print()
    print(
        tree.publish_set(
            miner=Miner.ATTACKER,
            blocks=[blocks[1], blocks[3]],
            edges={blocks[1]: blocks[0], blocks[3]: blocks[1]}
        )
    )
    print()

    print()
    print(
        tree.publish_set(
            miner=Miner.HONEST,
            blocks=[blocks[4]],
            edges={blocks[4]: blocks[3]}
        )
    )
    print()

    print()
    print("~~ capitulate by relabeling 3 to 0 (and 4 to 1) ~~")
    print()

    print()
    print(tree.capitulate(blocks[3]))
    print()