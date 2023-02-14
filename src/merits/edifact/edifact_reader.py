from typing import Dict, Iterable, List, Optional

from merits.edifact.data_handler import DataHandler
from merits.edifact.definition_model import Definition
from merits.edifact.object_model import DataLeaf, DataBranch
from merits.edifact.segment_format import SegmentFormat
from merits.edifact.segment_reader import SegmentReader
from merits.edifact.state_machine import StateMachine, State, Transition
from merits.exceptions import MeritsException


class EdifactReader(object):
    """
    This class parses an EDIFACT file and outputs to a DataHandler.
    """

    def __init__(
            self,
            definition: Definition,
    ):
        """

        :param definition: the definition of the specific EDIFACT structure and formats.
        """
        self._definition = definition

        self._main_separator = self._definition.config.separators[0]
        self._state_machine: StateMachine = StateMachine(
            definition=self._definition,
        )
        self._path_2_segment_reader: Dict[str, SegmentReader] = {}
        self._stack: List[State] = []

    def read(
            self,
            segments: Iterable[str],
            data_handler: DataHandler,
    ) -> None:
        """
        Parses the segments and outputs the results to the data_handler.
        :param segments:
        :param data_handler:
        :return:
        """
        # Reset stack and state machine.
        self._stack_push(self._state_machine.begin_state)
        self._state_machine.state = self._state_machine.begin_state

        segment_count = 0
        for segment_idx, segment in enumerate(segments):
            if not segment:
                # Skip empty lines (at the end of the file).
                continue
            segment_count += 1
            segment_name = segment[:3]
            transitions, err_msg = self._state_machine.handle(segment_name=segment_name)
            if err_msg:
                raise MeritsException(
                    f'Illegal segment at line {segment_idx + 1} coming from state '
                    f'{self._state_machine.state.node.node_id} {self._state_machine.state.path}'
                    f': {err_msg}'
                )
            self._transition(
                transitions=transitions,
                data_handler=data_handler,
                segment_idx=segment_idx,
                segment=segment,
            )
        # Exit to root state.
        transitions, err_msg = self._state_machine.finish()
        if err_msg:
            raise MeritsException(
                f'Could not finalize coming from state '
                f'{self._state_machine.state.node.node_id} {self._state_machine.state.path}'
                f': {err_msg}'
            )
        self._transition(
            transitions=transitions,
            data_handler=data_handler,
            segment_idx=segment_count,
            segment=None,
        )

    def _transition(
            self,
            transitions: List[Transition],
            data_handler: DataHandler,
            segment_idx: int,
            segment: Optional[str],
    ):
        for transition in transitions:
            if transition.exit:
                state = transition.exit
                self._stack_pop(state)
                if state.is_group():
                    data_handler.on_exit_branch(path=state.path)
                else:
                    data_handler.on_exit_leaf(path=state.path)
            if transition.enter:
                state = transition.enter
                if state.is_group():
                    data_handler.on_enter_branch(DataBranch(path=state.path))
                elif segment:
                    data_leaf: DataLeaf = self._read_segment(
                        segment=segment,
                        state=state,
                    )
                    if data_leaf.error:
                        raise MeritsException(
                            f'Failed to read line {segment_idx + 1} as segment type {state}: {data_leaf.error}'
                        )
                    data_handler.on_enter_leaf(leaf=data_leaf)
                else:
                    # No segment means entering the end state: do nothing.
                    pass
                self._stack_push(state)

    def _stack_pop(self, state: State):
        if not self._stack:
            raise MeritsException(
                f'Cannot exit state {state}: currently in root.'
            )
        if self._stack[-1] != state:
            raise MeritsException(
                f'Cannot exit state {state}: not top of stack {[str(state) for state in self._stack]}.'
            )
        self._stack.pop()

    def _stack_push(self, state: State):
        if self._stack:
            parent_state = self._stack[-1]
            if state not in parent_state.child_state_list:
                raise MeritsException(
                    f'Cannot enter state {state}: it is no child of current top of'
                    f' stack {[str(state) for state in self._stack]}.'
                )
        self._stack.append(state)

    def _read_segment(
            self,
            segment: str,
            state: State,
    ) -> DataLeaf:
        path = state.path
        segment_reader = self._path_2_segment_reader.get(path)
        if not segment_reader:
            segment_format = SegmentFormat(
                definition=state.segment,
                config=self._definition.config,
            )
            segment_reader = SegmentReader(
                path=path,
                segment_format=segment_format,
            )
            self._path_2_segment_reader[path] = segment_reader
        result = segment_reader.from_edifact(edifact_segment=segment)
        return result
