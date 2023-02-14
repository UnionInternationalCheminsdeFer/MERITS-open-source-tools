from typing import List

from merits.edifact.collector import Collector


class CollectorInMemory(Collector):
    """
    This implementation collects the segments in memory.
    """

    def __init__(self):
        super().__init__()
        self._segment_list: List[str] = []
        "All segments collected without end-of-line."

    def collect(self, edifact_segment: str) -> None:
        """
        Implements collect method and removes any new-line ("\n" and "\r") characters from the edifact_segment
        :param edifact_segment:
        :return:
        """
        clean_segment = edifact_segment.replace("\n", "").replace("\r", "")
        self._segment_list.append(clean_segment)

    def segment_count(self) -> int:
        return len(self._segment_list)

    def get(self, line_separator: str = "\n") -> str:
        """
        Gives the collected segments as one string. By default, the segments are separated by a new line character
        :param line_separator:
        :return:
        """
        return line_separator.join(self._segment_list) + line_separator
