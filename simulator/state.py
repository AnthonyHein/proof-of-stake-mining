from typing import List, Tuple, Type, Union

from action import Action
from block import Block
from block_utils import *
from miner import Miner
from tree import Tree

class State:

    def __init__(self,
                 tree: Tree = None,
                 unpublished_blocks: dict[Miner, List[Block]] = None,
                 rounds_mined_on: dict[Miner, List[int]] = None) -> None:
        """
        Maintains the state of the mining game.
        """

        if tree is not None and not isinstance(tree, Tree):
            raise TypeError("State.__init__: `tree` must be None or of type `Tree`")
        if unpublished_blocks is not None and not isinstance(unpublished_blocks, dict):
            raise TypeError("State.__init__: `unpublished_blocks` must be None or of type `dict[Miner, List[Block]]`")
        if unpublished_blocks is not None and not all(isinstance(k, Miner) and isinstance(v, list) for k, v in unpublished_blocks.items()):
            raise TypeError("State.__init__: `unpublished_blocks` must be None or of type `dict[Miner, List[Block]]`")
        if unpublished_blocks is not None and not all([Miner.ATTACKER in unpublished_blocks, Miner.HONEST in unpublished_blocks]):
            raise TypeError("State.__init__: `unpublished_blocks` must be None or of type `dict[Miner, List[Block]]`")
        if unpublished_blocks is not None and not all(isinstance(block, Block) for block in unpublished_blocks[Miner.ATTACKER]):
            raise TypeError("State.__init__: `unpublished_blocks` must be None or of type `dict[Miner, List[Block]]`")
        if unpublished_blocks is not None and not all(isinstance(block, Block) for block in unpublished_blocks[Miner.HONEST]):
            raise TypeError("State.__init__: `unpublished_blocks` must be None or of type `dict[Miner, List[Block]]`")
        if rounds_mined_on is not None and not isinstance(rounds_mined_on, dict):
            raise TypeError("State.__init__: `rounds_mined_on` must be None or of type `dict[Miner, List[int]]`")
        if rounds_mined_on is not None and not all(isinstance(k, Miner) and isinstance(v, list) for k, v in rounds_mined_on.items()):
            raise TypeError("State.__init__: `rounds_mined_on` must be None or of type `dict[Miner, List[int]]`")
        if rounds_mined_on is not None and not all([Miner.ATTACKER in rounds_mined_on, Miner.HONEST in rounds_mined_on]):
            raise TypeError("State.__init__: `rounds_mined_on` must be None or of type `dict[Miner, List[int]]`")
        if rounds_mined_on is not None and not all(isinstance(block, int) for block in rounds_mined_on[Miner.ATTACKER]):
            raise TypeError("State.__init__: `rounds_mined_on` must be None or of type `dict[Miner, List[int]]`")
        if unpublished_blocks is not None and not all(isinstance(block, int) for block in rounds_mined_on[Miner.HONEST]):
            raise TypeError("State.__init__: `rounds_mined_on` must be None or of type `dict[Miner, List[int]]`")

        if tree is not None:
            self.tree = tree.copy()
            
        else:
            self.tree: Tree = Tree()

        if unpublished_blocks is not None:
            self.unpublished_blocks = {
                Miner.ATTACKER: [block.copy() for block in unpublished_blocks[Miner.ATTACKER]],
                Miner.HONEST: [block.copy() for block in unpublished_blocks[Miner.HONEST]],
            }
        else:
            self.unpublished_blocks: dict[Miner, List[Block]] = {
                Miner.ATTACKER: [],
                Miner.HONEST: [],
            }

        if rounds_mined_on is not None:
            self.rounds_mined_on = rounds_mined_on.copy()
        else:
            self.rounds_mined_on: dict[Miner, List[int]] = {
                Miner.ATTACKER: [],
                Miner.HONEST: [],
            }

    def copy(self) -> 'State':
        """
        Returns a _deep_ copy of this state.
        """
        return State(self.tree, self.unpublished_blocks, self.rounds_mined_on)

    def capitulate(self, genesis: Block) -> 'State':
        """
        Modify the state so that the block `genesis` is effectively the genesis
        block from all strategies point of view; return the result.
        """

        if not isinstance(genesis, Block):
            raise TypeError("State.capitulate: `genesis` must be of type `Block`")
        if genesis not in self.tree.blocks:
            raise ValueError("State.capiulate: `genesis` must be an existing block in the tree")

        genesis_prev_height = genesis.height
        genesis_prev_created_at = genesis.created_at

        self.tree = self.tree.capitulate(genesis)

        self.unpublished_blocks = {
            Miner.ATTACKER: [
                relabel_block(block, genesis_prev_height, genesis_prev_created_at, False)
                for block
                in self.unpublished_blocks[Miner.ATTACKER]
                if block.created_at > genesis_prev_created_at
            ],
            Miner.HONEST: [
                relabel_block(block, genesis_prev_height, genesis_prev_created_at, False)
                for block
                in self.unpublished_blocks[Miner.HONEST]
                if block.created_at > genesis_prev_created_at
            ],
        }
        
        self.rounds_mined_on = {
            Miner.ATTACKER: [
                created_at - genesis_prev_created_at
                for created_at
                in self.rounds_mined_on[Miner.ATTACKER]
                if created_at > genesis_prev_created_at
            ],
            Miner.HONEST: [
                created_at - genesis_prev_created_at
                for created_at
                in self.rounds_mined_on[Miner.HONEST]
                if created_at > genesis_prev_created_at
            ],
        }

        return self
    
    def mine_block(self, block: Block) -> 'State':
        """
        Modify the state to include the newly mined block `block` and return the result.
        """
        if not isinstance(block, Block): 
            raise TypeError("State.mine_block: `block` must be of type `Block`")
        if block in self.tree.blocks or \
           block in self.unpublished_blocks[Miner.ATTACKER] or \
           block in self.unpublished_blocks[Miner.HONEST]:
            raise ValueError("State.mine_block: `block` must be new to this game state")

        self.unpublished_blocks[block.miner].append(block)
        self.rounds_mined_on[block.miner].append(block.created_at)

        return self

    def _wait(self, args: None) -> 'State':
        """
        Execute `Action.WAIT` on the current state and return the result.
        i.e., do nothing and return `self`.
        """
        if args != None:
            raise TypeError("State._wait: `args` must be `None` (to confirm intention)")
        
        return self

    def _publish_set(self, args: Tuple[Miner, List[Block], dict[Block, Block]]):
        """
        Execute `Action.PUBLISH_SET` with arguments specified by `args` on the state
        and return the result.
        """
        if not isinstance(args, tuple):
            raise TypeError("State._publish_set: `args` must be a 3-tuple")
        if len(args) != 3:
            raise TypeError("State._publish_set: `args` must be a 3-tuple")
        if not isinstance(args[0], Miner):
            raise TypeError("State._publish_set: `args[0]` must be of type `Miner`")
        if not isinstance(args[1], list):
            raise TypeError("State._publish_set: `args[1]` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in args[1]):
            raise TypeError("State._publish_set: `args[1]` must be of type `List[Block]`")
        if not isinstance(args[2], dict):
            raise TypeError("State._publish_set: `args[2]` must be of type `dict[Block, Block]`")
        if not all(isinstance(k, Block) and isinstance(v, Block) for k, v in args[2].items()):
            raise TypeError("State._publish_set: `args[2]` must be of type `dict[Block, Block]`")

        self.tree = self.tree.publish_set(args[0], args[1], args[2])
        self.unpublished_blocks[args[0]] = [
            block
            for block
            in self.unpublished_blocks[args[0]]
            if block not in args[1]
        ]

        return self


    def _publish_path(self, args: Tuple[Miner, List[Block], Block]):
        """
        Execute `Action.PUBLISH_PATH` with arguments specified by `args` on the state
        and return the result.
        """
        if not isinstance(args, tuple):
            raise TypeError("State._publish_path: `args` must be a 3-tuple")
        if len(args) != 3:
            raise TypeError("State._publish_path: `args` must be a 3-tuple")
        if not isinstance(args[0], Miner):
            raise TypeError("State._publish_path: `args[0]` must be of type `Miner`")
        if not isinstance(args[1], list):
            raise TypeError("State._publish_path: `args[1]` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in args[1]):
            raise TypeError("State._publish_path: `args[1]` must be of type `List[Block]`")
        if not isinstance(args[2], Block):
            raise TypeError("State._publish_path: `args[2]` must be of type `Block`")

        self.tree = self.tree.publish_path(args[0], args[1], args[2])
        self.unpublished_blocks[args[0]] = [
            block
            for block
            in self.unpublished_blocks[args[0]]
            if block not in args[1]
        ]

        return self

    def _publish(self, args: Tuple[Miner, List[Block], int, Block]):
        """"
        Execute `Action.PUBLISH` with arguments specified by `args` on the state
        and return the result.
        """
        if not isinstance(args, tuple):
            raise TypeError("State._publish: `args` must be a 3-tuple")
        if len(args) != 4:
            raise TypeError("State._publish: `args` must be a 3-tuple")
        if not isinstance(args[0], Miner):
            raise TypeError("State._publish: `args[0]` must be of type `Miner`")
        if not isinstance(args[1], list):
            raise TypeError("State._publish: `args[1]` must be of type `List[Block]`")
        if not all(isinstance(block, Block) for block in args[1]):
            raise TypeError("State._publish: `args[1]` must be of type `List[Block]`")
        if not isinstance(args[2], int):
            raise TypeError("State._publish: `args[2]` must be of type `int`")
        if not isinstance(args[3], Block):
            raise TypeError("State._publish: `args[3]` must be of type `Block`")
        
        self.tree = self.tree.publish(args[0], args[1], args[2], args[3])
        self.unpublished_blocks[args[0]] = [
            block
            for block
            in self.unpublished_blocks[args[0]]
            if block not in sort_blocks(args[1], reverse=False)[:args[2]]
        ]

        return self

    def take_action(
        self,
        action_w_args: Union[Tuple[Action, None],
                             Tuple[Action, Tuple[Miner, List[Block], dict[Block, Block]]],
                             Tuple[Action, Tuple[Miner, List[Block], Block]],
                             Tuple[Action, Tuple[Miner, List[Block], int, Block]]]
    ) -> 'State':
        """
        Execute the action at `action_w_args[0]` with arguments specified by the
        `action_w_args[1]` on this state and return the result.
        """
        if not isinstance(action_w_args, tuple):
            raise TypeError("State.take_action: `action_w_args` must be a 2-tuple")
        if len(action_w_args) != 2:
            raise TypeError("State.take_action: `action_w_args` must be a 2-tuple")
        if not isinstance(action_w_args[0], Action):
            raise TypeError("State.take_action: `action_w_args[0]` must be of type `Action`")

        action, args = action_w_args

        ACTION_TO_HELPER = {
            Action.WAIT: self._wait,
            Action.PUBLISH_SET: self._publish_set,
            Action.PUBLISH_PATH: self._publish_path,
            Action.PUBLISH: self._publish,
        }
 
        return ACTION_TO_HELPER[action](args)

    def __repr__(self) -> str:
        """
        Return a string representing the current state.
        """

        s = ""

        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        s += "~ STATE START                                              ~\n"
        s += "~                                                          ~\n"
        s += "~                                                          ~\n"
        s += "~ Tree                                                     ~\n"
        s += "~                                                          ~\n"
        s += str(self.tree)
        s += "~                                                          ~\n"
        s += "~ Unpublished blocks:                                      ~\n"
        s += "~                                                          ~\n"
        s +=f"~ Attacker: {str(self.unpublished_blocks[Miner.ATTACKER]): <47}~\n"
        s +=f"~ Honest: {str(self.unpublished_blocks[Miner.HONEST]): <49}~\n"
        s += "~                                                          ~\n"
        s += "~ Rounds mined on:                                         ~\n"
        s += "~                                                          ~\n"
        s +=f"~ Attacker: {str(self.rounds_mined_on[Miner.ATTACKER]): <47}~\n"
        s +=f"~ Honest: {str(self.rounds_mined_on[Miner.HONEST]): <49}~\n"
        s += "~                                                          ~\n"
        s += "~                                                          ~\n"
        s += "~ STATE END                                                ~\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

        return s
        

if __name__ == "__main__":

    state = State()

    