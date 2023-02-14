from abc import ABC, abstractmethod


class Collector(ABC):
    """
    This class gathers EDIFACT segments.
    """

    @abstractmethod
    def collect(self, edifact_segment: str) -> None:
        """
        Adds one EDIFACT segment to the collection.
        :param edifact_segment:
        :return:
        """
        pass

    @abstractmethod
    def segment_count(self) -> int:
        """
        Gives the number of segments that has been collected.
        :return:
        """
        pass
