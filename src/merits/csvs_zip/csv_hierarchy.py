import dataclasses
from collections import defaultdict
from typing import Optional, List, Collection, Dict

from merits.exceptions import MeritsException


class CsvTable(object):
    """
    This class represents a single CSV table definition (not the data) in a CsvHierarchy.
    """

    def __init__(
            self,
            csv_file_name: str,
            id_name: str,
            parent: Optional["CsvTable"] = None,
            field_name_list: Optional[List[str]] = None
    ):
        """

        :param csv_file_name: the file name without (parent) directories
        :param id_name: the header of the column that will contain the row ID
        :param parent: the parent iff this is not the metadata nor the root table
        :param field_name_list: the headers/field names
        """
        self.csv_file_name = csv_file_name
        self.id_name: str = id_name
        self.parent: Optional["CsvTable"] = parent
        self.field_name_list = field_name_list

    @staticmethod
    def from_dataclass(
            csv_file_name: str,
            datacls,
            parent: Optional["CsvTable"] = None,
    ) -> "CsvTable":
        """
        Constructs a CsvTable from a dataclass. The datacls represents one row in the CSV file. The first field must be
        the row ID field!
        :param csv_file_name:
        :param datacls:
        :param parent:
        :return:
        """
        field_name_list = [
            field.name
            for field in dataclasses.fields(datacls)
        ]
        id_name = field_name_list[0]
        return CsvTable(
            csv_file_name=csv_file_name,
            id_name=id_name,
            parent=parent,
            field_name_list=field_name_list
        )

    def check_field_names(self, headers: Collection[str]) -> None:
        """
        To detect typos, this raises a MeritsException if headers differs from the expected field names.
        :param headers:
        :return:
        :raises MeritsException:
        """
        if self.field_name_list:
            expected = set(self.field_name_list)
            actual = set(headers)
            missing_fields = expected - actual
            if missing_fields:
                raise MeritsException(
                    f'Missing in {self.csv_file_name} fields {list(missing_fields)}.'
                )
            extra_fields = actual - expected
            if extra_fields:
                raise MeritsException(
                    f'Found in {self.csv_file_name} extra fields {list(extra_fields)}.'
                )


class CsvHierarchy(object):
    """
    This class defines a tree of CSV tables plus one metadata table. Every child table must contain a column with the
    same name as its parents ID row and as value the parent row's ID. There must be only one root table so all tables
    except the meta and the root must have a parent.
    """

    def __init__(
            self,
            csv_table_list: List[CsvTable],
            meta_file_name: str,
    ):
        """

        :param csv_table_list: all tables, of which one meta (meta.csv_file_name = meta_file_name) and one root
            (root.parent = None)
        :param meta_file_name: the csv_file_name of the meta table
        """
        self.meta_file_name = meta_file_name
        "The csv_file_name of the meta table."
        meta_tables = [
            table
            for table in csv_table_list
            if table.csv_file_name == self.meta_file_name
        ]
        if len(meta_tables) != 1:
            raise MeritsException(
                f'Expected exactly one meta table ({self.meta_file_name}) but found {meta_tables}.'
            )
        self.meta_table = meta_tables[0]
        "The CsvTable object that represents the meta table."

        self.csv_file_name_2_table: Dict[str, CsvTable] = {
            table.csv_file_name: table
            for table in csv_table_list
            if table.csv_file_name != self.meta_file_name
        }
        "Lookup by csv_file_name only of non-meta tables."
        self.id_name_2_table: Dict[str, CsvTable] = {
            table.id_name: table
            for table in csv_table_list
            if table.csv_file_name != self.meta_file_name
        }
        "Lookup by ID field name only of non-meta tables."
        self.csv_file_name_2_children: Dict[str, List[CsvTable]] = defaultdict(list)
        "Lookup only of non-meta tables."
        for table in csv_table_list:
            if table.parent:
                self.csv_file_name_2_children[table.parent.csv_file_name].append(table)
        roots = [
            table
            for table in csv_table_list
            if (
                    table.csv_file_name != self.meta_file_name
                    and table.parent is None
            )
        ]
        if len(roots) != 1:
            raise MeritsException(
                f'Expected exactly one root but found {roots}.'
            )
        self.root_table = roots[0]
        "The CsvTable that represents the root table."
