from abc import ABC, abstractmethod

from merits.edifact.object_model import DataLeaf, DataBranch


class DataHandler(ABC):
    """
    This defines an interface for handling parsed EDIFACT data
    """

    @abstractmethod
    def on_enter_branch(
            self,
            branch: DataBranch,
    ) -> None:
        """
        This method is called when a EDIFACT group was entered. Note that the child_list will be None, because the
        children will be provided in separate calls to the DataHandler methods.
        :param branch:
        :return:
        """
        # Note to developers: Currently, only the path is set in the DataBranch object. In the future fields can be
        # added to DataBranch without breaking existing implementations of this DataHandler. If only the path would be
        # given as a parameter, then such an extension would be impossible.
        pass

    @abstractmethod
    def on_exit_branch(
            self,
            path: str,
    ) -> None:
        """
        This method is called when a EDIFACT group is left.
        :param path:
        :return:
        """
        pass

    @abstractmethod
    def on_enter_leaf(
            self,
            leaf: DataLeaf,
    ):
        """
        This method is called when an EDIFACT segment is entered. This call will always be directly followed by a call
        to on_exit_leaf with the same path.
        :param leaf:
        :return:
        """
        pass

    @abstractmethod
    def on_exit_leaf(
            self,
            path: str,
    ):
        """
        This method is called when an EDIFACT segment is left. This will always directly follow a call to on_enter_leaf
        with the same path.
        :param path:
        :return:
        """
        pass
