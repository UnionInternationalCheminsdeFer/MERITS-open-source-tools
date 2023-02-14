from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List

from merits import common
from merits.edifact.definition_model import Definition, Node, Segment
from merits.exceptions import MeritsException

logger = common.get_logger(__file__)


@dataclass
class Transition:
    exit: Optional["State"]
    "Go up the tree."
    enter: Optional["State"]
    "Go down the tree to destination state."

    def __str__(self):
        return f'ex={self.exit}, in={self.enter}'


@dataclass
class State:
    """
    A state represents a location/node in the structure of the EDIFACT definition. It holds information about the
    node definition and about the next state if a trigger is encountered.
    """
    path: str
    "The definition Node.name's joined by '/'. For example '2_PRD/4_POP/POP"
    node: Node
    "The definition node."
    segment: Optional[Segment]
    "The segment definition."
    child_state_list: List["State"]
    parent: Optional["State"]
    trigger: Optional[str]
    "The segment name that can trigger entering this State. For a group it is the name of the first child."
    _segment_name_2_transition: Optional[Dict[str, Transition]] = None
    """
    Transition represented by the name of the encountered segment. An empty string as segment_name is used for the 
    transitioning to the parent state. Segment names that are directly reachable from the current state are delegated 
    to the parent.
    """

    def __str__(self):
        return f'{self.node.node_id}@{self.path}'

    @staticmethod
    def get_trigger_to_group_first() -> str:
        """
        Gives a fixed trigger string that is used as a key to the first child in this group State.
        :return:
        """
        return "to-group-first"

    @staticmethod
    def get_trigger_start() -> str:
        """
        Gives a fixed string that is used as the name and node_id of the beginning state. The beginning state is a
        concept internal to the state machine. It is BEFORE the first segment is encountered and does NOT exist in the
        EDIFACT definition.
        :return:
        """
        return "start"

    @staticmethod
    def get_trigger_final():
        """
        Gives a fixed string that is used as the name and node_id of the end state. The end state is a concept
        internal to the state machine. It is the end of file is encountered and does NOT exist in the EDIFACT
        definition.
        :return:
        """
        return "final"

    def add_transition(self, trigger: str, transition: Transition) -> None:
        """
        Adds a Transition from this state to a next one. The trigger must be unique for this State.
        :param trigger:
        :param transition:
        :return:
        """
        if self._segment_name_2_transition is None:
            self._segment_name_2_transition = {}
        if trigger in self._segment_name_2_transition:
            existing_transitions, err_msg = self.handle_trigger(trigger)
            if err_msg:
                existing_msg = err_msg
            else:
                existing_msg = "Unknown"
                if existing_transitions:
                    destination = existing_transitions[-1].enter
                    if destination:
                        existing_msg = str(destination)
            raise MeritsException(
                f'Trigger "{trigger}" for {self} already exists: {existing_msg}.'
            )
        self._segment_name_2_transition[trigger] = transition

    def is_group(self):
        """
        Tells if this State represents an EDIFACT group.
        :return:
        """
        return bool(self.child_state_list)

    def handle_trigger(
            self,
            segment_name: str,
    ) -> Tuple[
        List[Transition],
        Optional[str],
    ]:
        """
        Gives the route from the current state to the next triggered state. This may involve multiple transitions. For
        example in SKDUPD state "2_PRD/4_POP/POP" will respond to a "UIT" segment_name with transactions
        "2_PRD/4_POP/POP" ➔ "2_PRD/4_POP" ➔ "2_PRD" ➔ "UIT".

        If an error (for example a segment_name that is invalid at this state) is encountered, the nan error text is
        returned with an empty list as route.

        :param segment_name:
        :return: route from current state to triggered state, error text
        """
        transitions = []
        # Find transition by trigger.
        next_state: State = self
        next_transition = next_state._segment_name_2_transition.get(segment_name)
        count = 0
        while not next_transition:
            count += 1
            group_leave_transition = next_state._segment_name_2_transition.get("")
            if group_leave_transition:
                transitions.append(group_leave_transition)
                next_state = group_leave_transition.exit.parent
            else:
                error_msg = f'Invalid trigger "{segment_name}" at node {self.node.node_id} at path {self.path}.'
                logger.error(error_msg)
                return [], error_msg
            next_transition = next_state._segment_name_2_transition.get(segment_name)
        transitions.append(next_transition)
        destination_state = next_transition.enter
        if destination_state and destination_state.is_group():
            in_group_transitions, err_msg = destination_state.handle_trigger(self.get_trigger_to_group_first())
            if err_msg:
                error_msg = (
                    f'Could not go to first group member:'
                    f' trigger "{segment_name}" from {self}'
                    f' transitions {[str(trans) for trans in transitions]}.'
                )
                logger.error(error_msg)
                return [], error_msg
            transitions.append(in_group_transitions[0])
        return transitions, None


class StateMachine(object):
    """
    This class converts a segment name to a full path during parsing. For example in SKDUPD "ASD" may be "2_PRD/ASD",
    "2_PRD/3_SER/ASD", "2_PRD/4_POP/ASD", "2_PRD/4_POP/7_POR/ASD", "2_PRD/4_POP/9_ODI/ASD", or
    "2_PRD/4_POP/9_ODI/10_SER/ASD" depending on which segments have been encountered before.

    It also gives the transitions to get from the last path/State to the current.
    """

    def __init__(
            self,
            definition: Definition,
    ):
        self.definition = definition

        self.node_id_2_segment: Dict[str, Segment] = {
            seg.node_id: seg
            for seg in self.definition.segment_list
        }
        self.top_state_list: Optional[List[State]] = None
        self.begin_state: Optional[State] = None
        self.end_state: Optional[State] = None
        self.state: Optional[State] = None
        self._after_new()

    def handle(
            self,
            segment_name: str,
    ) -> Tuple[
        List[Transition],
        Optional[str],
    ]:
        """
        Call this method when encountering a segment during parsing of an EDIFACT file.
        :param segment_name: the name of the encountered segment. Foe example "ASD"
        :return: route from current state to triggered state, error text
        """
        transitions, err_msg = self.state.handle_trigger(segment_name)
        if not err_msg:
            destination = transitions[-1]
            self.state = destination.enter if destination.enter else destination.exit
        return transitions, err_msg

    def finish(self) -> Tuple[
        List[Transition],
        Optional[str],
    ]:
        """
        Call this method when you have reached the end of your EDIFACT file. This will give the transitions to the
        end state.
        :return:
        """
        transitions, err_msg = self.handle(State.get_trigger_final())
        if self.state != self.end_state:
            err_msg = "Failed final transition to end state." + (f" {err_msg}" if err_msg else '')
        return transitions, err_msg

    def reset(self) -> None:
        """
        Resets this state machine to the beginning state.
        :return: None
        """
        self.state = self.begin_state

    def _create_states(
            self,
            root_node: Node,
    ) -> List[State]:
        top_nodes = [
            Node(
                name=State.get_trigger_start(),
                node_id=State.get_trigger_start(),
                occurrences_min=1,
                occurrences_max=1
            ),
        ]
        top_nodes.extend(root_node.child_list)
        top_nodes.append(
            Node(
                name=State.get_trigger_final(),
                node_id=State.get_trigger_final(),
                occurrences_min=1,
                occurrences_max=1
            ),
        )
        top_state_list = self._create_and_add_child_states(
            child_node_list=top_nodes,
            parent_state=None,
        )
        return top_state_list

    def _create_and_add_child_states(
            self,
            child_node_list: List[Node],
            parent_state: Optional[State],
    ) -> List[State]:
        child_state_list = []
        path_prefix = parent_state.path + "/" if parent_state else ""
        for child_node in child_node_list:
            child_is_group = bool(child_node.child_list)
            if child_is_group:
                trigger = child_node.child_list[0].name
            else:
                trigger = child_node.name
            child_path: str = path_prefix + child_node.name
            child_state = State(
                parent=parent_state,
                trigger=trigger,
                path=child_path,
                node=child_node,
                # The segment is None for groups.
                segment=self.node_id_2_segment.get(child_node.node_id),
                child_state_list=[],
            )
            child_state_list.append(child_state)
            if parent_state:
                parent_state.child_state_list.append(child_state)
            if child_is_group:
                self._create_and_add_child_states(
                    child_node_list=child_state.node.child_list,
                    parent_state=child_state,
                )
        return child_state_list

    def _link_states(self):
        for state in self.top_state_list:
            self._link_next_states(
                state=state,
                siblings=self.top_state_list,
            )

    def _link_next_states(
            self,
            state: State,
            siblings: List[State],
    ) -> None:
        if state.is_group():
            # Add transition to first, always mandatory child.
            state.add_transition(
                State.get_trigger_to_group_first(),
                Transition(
                    exit=None,
                    enter=state.child_state_list[0],
                ),
            )
            # Process child states.
            for child_state in state.child_state_list:
                self._link_next_states(
                    state=child_state,
                    siblings=state.child_state_list,
                )
        # Add transition to self if repetition is allowed.
        if state.node.occurrences_max > 1:
            state.add_transition(
                state.trigger,
                Transition(
                    exit=state,
                    enter=state,
                ),
            )
        # Add transitions to younger siblings until mandatory sibling.
        younger_siblings = siblings[siblings.index(state) + 1:]
        for sibling in younger_siblings:
            state.add_transition(
                sibling.trigger,
                Transition(
                    exit=state,
                    enter=sibling,
                ),
            )
            if sibling.node.occurrences_min:
                # Sibling is mandatory: further younger siblings are not reachable from this state.
                break
        # Add transition to parent, if exists.
        if state.parent:
            state.add_transition(
                "",
                Transition(
                    exit=state,
                    enter=None,
                ),
            )

    def _after_new(self) -> None:
        self.top_state_list = self._create_states(
            root_node=self.definition.structure,
        )
        self.begin_state = self.top_state_list[0]
        self.end_state = self.top_state_list[-1]
        self.state = self.begin_state
        self._link_states()
