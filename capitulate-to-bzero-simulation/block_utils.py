from typing import List

from block import Block
from miner import Miner

def sort_blocks(blocks: List[Block], reverse: bool) -> List[Block]:
    """
    Given a list of blocks `blocks`, return them in sorted order by their
    `created_at` timestamp; the order is reversed if `reverse` is true.
    """
    if not isinstance(blocks, list):
        raise TypeError("block_utils.sort_blocks: `blocks` must be of type `List[Block]`")
    if not all(isinstance(block, Block) for block in blocks):
        raise TypeError("block_utils.sort_blocks: `blocks` must be of type `List[Block]`")

    return sorted(blocks, key=lambda block: block.created_at, reverse=reverse)

def relabel_block(block: Block,
                  genesis_prev_height: int,
                  genesis_prev_created_at: int,
                  is_genesis: bool) -> Block:
    """
    Given the previous height `genesis_prev_height` and previous timestep of creation
    `genesis_prev_created_at` of the block we will now be relabeling as the genesis block,
    relabel this block `block` accordingly. If this is the block we are relabeling as the
    genesis block, as indicated by `is_genesis`, do additional processing.
    """
    if not isinstance(block, Block):
        raise TypeError("block_utils.relabel_block: `block` must be of type `Block`")
    if not isinstance(genesis_prev_height, int):
        raise TypeError("block_utils.relabel_block: `genesis_prev_height` must be of type `int`")
    if not isinstance(genesis_prev_created_at, int):
        raise TypeError("block_utils.relabel_block: `genesis_prev_created_at` must be of type `int`")
    if not isinstance(is_genesis, bool):
        raise TypeError("block_utils.relabel_block: `is_genesis` must be of type `bool`")

    block.created_at = block.created_at - genesis_prev_created_at
    block.height = block.height - genesis_prev_height

    if is_genesis:
        block.miner = Miner.GENESIS
        block.parent = None

    return block