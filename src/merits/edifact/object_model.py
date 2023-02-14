"""
This module contains classes for object representations of data nodes in an EDIFACT file.
"""
from dataclasses import dataclass
from typing import List, Union, Dict, Optional

from merits.edifact.segment_format import SegmentFormat
from merits.exceptions import MeritsException


class DataLeaf(object):
    """
    This class represents data of a segment/non-group node in an EDIFACT file. It has a setter and a getter, that both
    check if field names are according to the segment format in the definition.
    """
    def __init__(
            self,
            path: str,
            segment_format: SegmentFormat,
    ):
        """

        :param path: the EDIFACT structural location as '/' separated string.
                        For example "Group_02/Group_04/POP"
        """
        self.path: str = path
        self.segment_format = segment_format
        self.error: Optional[str] = None
        self._name_2_value: Dict[str, str] = {}
        self._all_names = {
            field.name
            for field in self.segment_format.field_list
            # Exclude fields without name.
            if field.name
        }

    def set(
            self,
            name: str,
            value: str,
    ) -> None:
        """

        :param name: field name in segment format
        :param value: the value to store in this object
        :return: None
        :raise MeritsException: if name is not in the definition, or if value already set for name
        """
        if name in self._name_2_value:
            raise MeritsException(
                f'Failed to set "{name}"="{value}": already has value "{self._name_2_value[name]}".'
            )
        if name not in self._all_names:
            raise MeritsException(
                f'Failed to set "{name}"="{value}": name not in definition.'
            )
        self._name_2_value[name] = value

    def get(
            self,
            name: str,
            default: Optional[str] = "",
    ) -> Optional[str]:
        """
        Gives the value for the named entry.

        :param name: field name in segment format
        :param default: the return value if not set in the data.
        :return: the stored value or None
        :raise MeritsException: if name is not in the definition
        """
        if name not in self._all_names:
            raise MeritsException(
                f'Failed to get "{name}": name not in definition.'
            )
        return self._name_2_value.get(name, default)

    def get_all(self) -> Dict[str, str]:
        """
        For testing purposes: has no checks: do NOT use for application.
        :return:
        """
        return dict(self._name_2_value)


@dataclass
class DataBranch:
    """
    A DataBranch is always a group and can be child of another group.
    """
    path: str
    """
    The EDIFACT structural location as '/' separated string. 
    For example "2_PRD/4_POP/7_POR".
    """
    child_list: Optional[List[Union["DataBranch", DataLeaf]]] = None
    """
    A full object representation of an EDIFACT file will be a root DataBranch with the rest of the information in it's 
    offspring.
    """
