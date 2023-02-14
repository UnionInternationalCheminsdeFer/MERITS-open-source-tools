"""
This module contains classes that extract single string EDIFACT segment formats into objects usable in python.
"""
import string
from typing import List, Tuple, Optional

from merits.edifact.definition_model import Segment, Config


class Field(object):
    """
    This class represents one field in a segment format.
    """

    def __init__(
            self,
            name: str,
            level: int,
            expected_value: Optional[str] = None,
    ):
        self.name = name
        self.level = level
        self.expected_value = expected_value


# noinspection PyMethodMayBeStatic
class SegmentFormat(object):
    """
    An expanded representation of a segment definition's format string.
    """

    def __init__(
            self,
            definition: Segment,
            config: Config,
    ):
        """

        :param definition: a Segment from the definition of which the format will be parsed into an object
        representation
        :param config: the definition config. This will be stored by reference so separators can be changed later on.
            For example if the definition uses different separators than the data
        """
        self.definition = definition
        self.config = config
        self.name, self.field_list = self._parse_format()
        self.name_2_field = {
            field.name: field
            for field in self.field_list
        }

    def _parse_format(self) -> Tuple[
        str,
        List[Field],
    ]:
        separators = self.config.separators
        escape_char = self.config.escape_char
        terminator = self.config.segment_terminator
        # Remove all white space, tabs, new lines.
        plain_format = self.definition.format.translate({ord(c): None for c in string.whitespace})
        segment_name = None
        field_list = []
        buffer: List[str] = []
        "Collects segment_name or {name}={expected_value} characters."
        escaped: bool = False
        level = 1
        # Work through one character at a time.
        for c_idx, c in enumerate(plain_format):
            if not escaped and c == terminator:
                # End of segment indicator: finish up.
                break
            elif not escaped and c in separators:
                name_and_expected_value = "".join(buffer)
                buffer.clear()
                if segment_name:
                    field_list.append(self._create_field(name_and_expected_value, level=level))
                else:
                    segment_name = name_and_expected_value
                level = separators.index(c) + 1
            elif not escaped and c == escape_char:
                escaped = True
            else:
                buffer.append(c)
                escaped = False
        if buffer:
            # Add final bit of information in the buffer.
            name_and_expected_value = "".join(buffer)
            buffer.clear()
            if segment_name:
                field_list.append(self._create_field(name_and_expected_value, level=level))
            else:
                segment_name = name_and_expected_value
        return segment_name, field_list

    def _create_field(
            self,
            name_and_expected_value: str,
            level: int,
    ) -> Field:
        name, has_expected_value, expected_value = name_and_expected_value.partition("=")
        field = Field(
            name=name,
            level=level,
            expected_value=expected_value if has_expected_value else None,
        )
        return field
