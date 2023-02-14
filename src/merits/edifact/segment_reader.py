from typing import List

from merits.edifact.object_model import DataLeaf
from merits.edifact.segment_format import SegmentFormat
from merits.exceptions import MeritsException


class SegmentReader(object):
    """
    This class converts an EDIFACT segment string to an object representation DataLeaf.
    """

    def __init__(
            self,
            path: str,
            segment_format: SegmentFormat,
    ):
        """
        :param path: the path of this segment (needed in the created DataLeaf objects)
        :param segment_format: the segment format
        """
        self.path = path
        self.segment_format = segment_format

    def from_edifact(self, edifact_segment: str) -> DataLeaf:
        """
        Parses the edifact_segment string into a DataLeaf.

        If something goes wrong, then an error message will be set in the resulting DataLeaf.

        :param edifact_segment:
        :return:
        """
        separators = self.segment_format.config.separators
        escape_char = self.segment_format.config.escape_char
        terminator = self.segment_format.config.segment_terminator
        fields = self.segment_format.field_list
        data_leaf = DataLeaf(
            path=self.path,
            segment_format=self.segment_format,
        )
        buffer: List[str] = []
        "Collects value characters."
        field_idx = -1
        escaped: bool = False
        # Work through one character at a time.
        for c_idx, c in enumerate(edifact_segment):
            if not escaped and c == terminator:
                # End of segment indicator: finish up.
                break
            elif not escaped and c in separators:
                value = "".join(buffer)
                buffer.clear()
                self._set_field(
                    field_idx=field_idx,
                    value=value,
                    data_leaf=data_leaf,
                )
                if data_leaf.error:
                    # Abort further parsing.
                    return data_leaf

                # Continue to the next field of the level defined by the encountered separator.
                start_field_idx = field_idx
                next_level = separators.index(c) + 1
                field_idx += 1
                while field_idx < len(fields) and fields[field_idx].level > next_level:
                    field_idx += 1
                if field_idx >= len(fields) or fields[field_idx].level != next_level:
                    data_leaf.error = (
                        f'Unexpected separator "{c}" at {c_idx + 1}'
                        f' coming from field index {start_field_idx}'
                        f' "{fields[start_field_idx] if start_field_idx >= 0 else self.segment_format.name}".'
                    )
                    # Abort further parsing.
                    return data_leaf
            elif not escaped and c == escape_char:
                escaped = True
            else:
                buffer.append(c)
                escaped = False
        if buffer:
            # Add final bit of information in the buffer.
            value = "".join(buffer)
            buffer.clear()
            self._set_field(
                field_idx=field_idx,
                value=value,
                data_leaf=data_leaf,
            )

        return data_leaf

    def _set_field(
            self,
            field_idx: int,
            value: str,
            data_leaf: DataLeaf,
    ):
        """
        Does some checks and sets the field value
        :param field_idx:
        :param value:
        :param data_leaf: sets data_leaf.error if something went wrong. Sets the field value
        :return:
        """
        if field_idx < 0:
            if value != self.segment_format.name:
                # This would be a coding error: raise as exception.
                raise MeritsException(
                    f'Wrong segment name "{value}": expected "{self.segment_format.name}".'
                )
        else:
            field = self.segment_format.field_list[field_idx]
            field_name = field.name
            if field.expected_value and field.expected_value != value:
                # This would be an input error: return as error message for further handling.
                data_leaf.error = (
                    f'Expected value "{field.expected_value}" at field "{field_name}" but found "{value}".'
                )
            if field_name:
                data_leaf.set(
                    name=field_name,
                    value=value,
                )
