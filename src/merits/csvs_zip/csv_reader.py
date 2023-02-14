from typing import Optional, Dict

from merits.csvs_zip.csv_handler import CsvHandler
from merits.csvs_zip.csv_hierarchy import CsvTable, CsvHierarchy
from merits.csvs_zip.rows import Rows
from merits.exceptions import MeritsException


class CsvReader(object):
    """
    This class reads/parses a hierarchy of CSV files and calls a CsvHandler with each row followed by its child rows.
    If the columns in the CSV files mismatch the specifications in the CsvHierarchy a MeritsException will be raised.
    (CsvParser may have been a better name for this class, because it follows the pattern of forwarding data elements
    to a handler on the go instead of reading everything and presenting it as one data object.)
    """

    def __init__(
            self,
            csv_hierarchy: CsvHierarchy,
            csv_handler: CsvHandler,
    ):
        """

        :param csv_hierarchy: a definition of the hierarchy of CSV tables to expect
        :param csv_handler: a handler that will process the CSV rows
        """
        self.csv_hierarchy = csv_hierarchy
        self.csv_handler = csv_handler

    def read(
            self,
            csv_file_name_2_rows: Dict[str, Rows],
    ) -> None:
        """
        Reads the rows in the parent-then-children order to the self.csv_handler. Checks the file names and field names
        before calling the handler.
        :param csv_file_name_2_rows:
        :return:
        :raises MeritsException: if any of the checks went wrong
        """
        # Check file names.
        expected_files = set(self.csv_hierarchy.csv_file_name_2_table.keys())
        expected_files.add(self.csv_hierarchy.meta_file_name)
        actual_files = csv_file_name_2_rows.keys()
        missing_files = expected_files - actual_files
        if missing_files:
            raise MeritsException(
                f'Missing files {list(missing_files)}.'
            )
        extra_files = actual_files - expected_files
        if extra_files:
            raise MeritsException(
                f'Unexpected files {list(extra_files)}.'
            )
        # Check field names.
        for csv_file_name, rows in csv_file_name_2_rows.items():
            if csv_file_name == self.csv_hierarchy.meta_file_name:
                table = self.csv_hierarchy.meta_table
            else:
                table = self.csv_hierarchy.csv_file_name_2_table[csv_file_name]
            table.check_field_names(rows.headers())

        # Start with meta data.
        meta_file_name = self.csv_hierarchy.meta_file_name
        # In practice, we expect only one row in the metadata.
        meta_row = csv_file_name_2_rows[meta_file_name].peek()
        self.csv_handler.handle_begin(
            meta_data=meta_row,
        )

        # Read from the root table and recurse to child tables.
        self._read(
            parent_id=None,
            table=self.csv_hierarchy.root_table,
            csv_file_name_2_rows=csv_file_name_2_rows,
        )

        # End (again with the same meta-data)
        self.csv_handler.handle_end(
            meta_data=meta_row,
        )

    def _read(
            self,
            parent_id: Optional[str],
            table: CsvTable,
            csv_file_name_2_rows: Dict[str, Rows],
    ) -> None:
        """
        Recursive method to read parent-then-children and recurse to further offspring.
        :param parent_id: the value of the ID cell if any parent
        :param table: the table definition for which rows are to be handled
        :param csv_file_name_2_rows: all data
        :return:
        """
        rows = csv_file_name_2_rows[table.csv_file_name]

        while rows.has_more():
            # Peek at the row to see if it has the given parent_id.
            row = rows.peek()
            if parent_id:
                current_parent_id = row[table.parent.id_name]
                if current_parent_id != parent_id:
                    break
            # Same parent: continue handling row.
            row = rows.pop()
            self.csv_handler.handle_row(
                table.csv_file_name,
                row,
            )
            # Handle child table rows.
            child_list = self.csv_hierarchy.csv_file_name_2_children[table.csv_file_name]
            row_id = row[table.id_name]
            for child in child_list:
                self._read(
                    parent_id=row_id,
                    table=child,
                    csv_file_name_2_rows=csv_file_name_2_rows,
                )
