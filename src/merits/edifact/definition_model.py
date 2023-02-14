"""
This module contains the definition of an EDIFACT structure and segment format. It consists of dataclasses without
methods. This makes it easy to exchange or convert (to/from JSON).

Support for repetition of tags is limited to static number of repetitions.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Node:
    """
    This class represents a group or segment in an EDIFACT structure. The structure determines which segment names can
    be expected next if they should be interpreted as detail data of a parent node. See the UIC leaflet for examples.
    """
    node_id: str
    "A 4 digit ID that is unique within the tree."
    name: str
    """
    A (not unique) name (e.g. PRD, POP, POR, etc) that is more readable to some humans. For groups this is a numeric 
    string. For groups this should be {group_number}_{first_child_node_name}, for example 4_POP.
    """
    occurrences_min: int
    "The minimal number of occurrences of this node. Supported are only 0 and 1."
    occurrences_max: int
    "The maximum number of occurrences of this node. Supported are only 0 and 1."
    child_list: Optional[List["Node"]] = None
    "The child nodes, only if this is a group node."


@dataclass
class Tag:
    """
    NOT USED IN minimal viable product!
    This contains further information about tags. It can be used for documenting the tags and in the future more
    functionality may use this.
    """
    name: str
    "The name as it occurs in the format field in the Segment class (below)."
    tag_1: Optional[str] = None
    """
    As defined in the UIC leaflet.
    For multiple occurrences a `#` and a sequence number starting at 1 should be appended. 
    For example (in SKDUPD POR) E362#1.
    """
    tag_2: Optional[str] = None
    """
    As defined in the UIC leaflet.
    For multiple occurrences a `#` and a sequence number starting at 1 should be appended. 
    For example (in SKDUPD POR E362#1) 2002#1.
    """
    occurrences_min: Optional[int] = None
    "The minimal number of occurrences of this tag."
    occurrences_max: Optional[int] = None
    "The maximum number of occurrences of this tag."
    format: Optional[str] = None
    "'an' for alpha numeric, etc, see documentation."
    max_length: Optional[int] = None
    comment: Optional[str] = None


@dataclass
class Segment:
    """
    This defines the format of a segment.
    """
    node_id: str
    "Reference to Node.node_id."
    format: str
    """
    The definition of the segment as an EDIFACT string where the values are replaced by the field names.
    For example
    
    ASD
    +extra_service
            :first_time
            :last_time
            :
            :
            :
            :reservation
            :
            :
            :
            :
            :
            :
            :frequency
            :unit
    +period_qualifier
            :period
            :
            :days
    +week_days
    
    The white space and new lines may be present or absent. If indented, then top level should be '+', 
    second indent '*', and third indent ':'. (The '*' officially indicates repetition of tag-1 but is technically
    interpreted as just another level of separation. This has the same effect as long as the number of repetitions is 
    static.) A fourth level '/' is also supported. 
    
    Field names must be unique within the format.
    """
    name: Optional[str] = None
    """
    NOT USED IN minimal viable product!
    The name of the segment: PRD, POR, ASD, etc. This is optional as it can be deduced from the format.
    """
    tag_list: Optional[List[Tag]] = None
    """
    NOT USED IN minimal viable product!
    Extra information.
    """


@dataclass
class Config:
    segment_terminator: str = "'"
    separators: str = "+*:"
    "The separators to use when interpreting the segment format strings, order by level/depth in a single string."
    escape_char: str = "?"


@dataclass
class Definition:
    version: str
    "An indication of the type and/or version of the definition."
    structure: Node
    "The root node."
    segment_list: List[Segment]
    "The definitions of segments. These are linked to (non group) nodes in the structure by node_id."
    config: Config
