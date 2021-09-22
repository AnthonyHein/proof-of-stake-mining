from typing import List

from block import Block

def sort_blocks(blocks: List[Block], reverse: bool = True) -> List[Block]:
    """
    Given a list of blocks `blocks`, return them in sorted order by their
    `created_at` timestamp; the order is reversed if `reverse` is true
    """
    if not isinstance(blocks, list):
        raise TypeError("block_utils.sort_blocks: `blocks` must be of type `List[Block]`")
    if not all(isinstance(block, Block) for block in blocks):
        raise TypeError("block_utils.sort_blocks: `blocks` must be of type `List[Block]`")

    return sorted(blocks, key=lambda block: block.created_at, reverse=reverse)