from typing import List, Optional

from merits.edifact.object_model import DataLeaf


class SegmentWriter(object):

    @staticmethod
    def to_edifact(leaf: DataLeaf) -> str:
        """
        This creates one EDIFACT segment string from a DataLeaf. The DataLeaf contains all the format specifications.
        :param leaf:
        :return:
        """
        segment_format = leaf.segment_format
        config = segment_format.config
        separators = config.separators
        escape_char = config.escape_char
        terminator = config.segment_terminator
        fields = segment_format.field_list

        result: List[str] = [terminator]
        "The result will build up in reversed order."
        buffer: List[str]
        current_level: Optional[int] = None
        for field in reversed(fields):
            level = field.level
            if field.name:
                value = leaf.get(field.name, None)
            else:
                value = None
            if value:
                # Escape special characters.
                value = value.replace(escape_char, escape_char + escape_char)
                for separator in separators:
                    value = value.replace(separator, escape_char + separator)
                value = value.replace(terminator, escape_char + terminator)
                # Set the value.
                result.append(value)
                current_level = level
            if current_level is not None and level <= current_level:
                result.append(separators[level - 1])
                current_level = level
        result.append(segment_format.name)
        # Put the result in regular order.
        result.reverse()
        return "".join(result)
