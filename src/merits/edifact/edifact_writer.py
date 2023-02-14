from typing import Dict, List, Optional

from merits.edifact.definition_model import Definition, Node
from merits.edifact.object_model import DataLeaf
from merits.edifact.segment_format import SegmentFormat, Field
from merits.edifact.segment_writer import SegmentWriter
from merits.edifact.state_machine import StateMachine
from merits.exceptions import MeritsException


class EdifactWriter(object):
    """
    This class knows all segment formats. It has a function that finds the correct segment format by a given path and
    converts a data dict to an EDIFACT segment string.
    """

    def __init__(
            self,
            definition: Definition,
    ):
        self._definition = definition
        self._config = self._definition.config
        self._node_id_2_segment_definition = {
            seg.node_id: seg
            for seg in self._definition.segment_list
        }
        self._path_2_segment_format: Dict[str, SegmentFormat] = {}
        for top_node in self._definition.structure.child_list:
            self._fill_path_2_segment_format(node=top_node, parent_path="")

        self._state_machine = StateMachine(
            definition=definition,
        )

    def _fill_path_2_segment_format(self, node: Node, parent_path: str) -> None:
        is_group = bool(node.child_list)
        if is_group:
            node_path = parent_path + node.name + "/"
            for child_node in node.child_list:
                self._fill_path_2_segment_format(node=child_node, parent_path=node_path)
        else:
            node_path = parent_path + node.name
            segment_definition = self._node_id_2_segment_definition.get(node.node_id)
            if not segment_definition:
                raise MeritsException(
                    f'Could not find segment {node.node_id} {node_path} in definition.'
                )
            self._path_2_segment_format[node_path] = SegmentFormat(
                definition=segment_definition,
                config=self._config,
            )

    def to_edifact(
            self,
            path: str,
            data: Dict[str, str],
            add_defaults_for: Optional[List[str]] = None,
    ) -> str:
        """
        Converts the data to an EDIFACT line of the correct format for the path.

        :param path: the path in the definition tree
        :param data: keys are names of fields in the segment definition
        :param add_defaults_for: names of fields that should be added with the default values from the segment
            definition
        :return: one EDIFACT line
        :raise MeritsException: if the path is unknown or is a group. If data contains an unknown field
        """
        segment_format = self._path_2_segment_format.get(path)
        if not segment_format:
            raise MeritsException(
                f'Could not find a format for segment at "{path}"'
            )
        # Check valid segment name
        transitions, err_msg = self._state_machine.handle(segment_format.name)
        if err_msg:
            raise MeritsException(
                f'Could not add "{path}" {data}: {err_msg}'
            )
        if path != transitions[-1].enter.path:
            raise MeritsException(
                f'Segment name expects path "{transitions[-1].enter.path}" but given is "{path}".'
            )

        leaf = DataLeaf(
            path=path,
            segment_format=segment_format,
        )
        if add_defaults_for:
            for default_name in add_defaults_for:
                field: Field = segment_format.name_2_field.get(default_name)
                if not field:
                    raise MeritsException(
                        f'No field "{default_name}" defined in "{path}".'
                    )
                if not field.expected_value:
                    raise MeritsException(
                        f'No expected/default value for field "{default_name}" defined in "{path}".'
                    )
                leaf.set(default_name, field.expected_value)
        for k, v in data.items():
            leaf.set(k, v)
        edifact = SegmentWriter.to_edifact(leaf)
        return edifact
