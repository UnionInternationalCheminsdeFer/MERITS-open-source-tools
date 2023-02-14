import dataclasses
from typing import Optional, Callable, Dict, List

from merits.csvs_zip.collector import Collector
from merits.edifact.data_handler import DataHandler
from merits.edifact.definition_model import Definition, Node
from merits.edifact.object_model import DataLeaf, DataBranch
from merits.exceptions import MeritsException
from merits.tsdupd.csv_model import Stop, Synonym, Mct, Footpath, Meta
from merits.tsdupd.definition import (
    META_FILE_NAME, STOP_FILE_NAME, SYNONYM_FILE_NAME, MCT_FILE_NAME, FOOTPATH_FILE_NAME,
)


class DataHandlerToCsvCollector(DataHandler):
    """
    This class contains the mapping from TSDUPD EDIFACT to CSV files. From the code it should be clear what happens.

    Normally, a group in EDIFACT relates to a row in CSV. The TSDUPD - CSV conversion has two deviating peculiarities.

    1. A row in TSDUPD_SYNONYM.csv relates to segment 2_ALS/IFT instead of a group in EDIFACT. This segment is only
    converted to a row in CSV if the first field has value "AGW".
    2. A row in TSDUPD_FOOTPATH.csv is related to group 2_ALS/5_RFR but only if the first field value is "AWN".
    """

    def __init__(
            self,
            csv_collector: Collector,
            definition: Optional[Definition],
    ):
        """

        :param csv_collector:
        :param definition: this helps to find typos in the paths
        """

        self._csv_collector = csv_collector
        self._next_stop_id = 1
        self._next_synonym_id = 1
        self._next_mct_id = 1
        self._next_footpath_id = 1
        self._meta: Optional[Meta] = None
        self._current_stop: Optional[Stop] = None
        self._current_synonym: Optional[Synonym] = None
        self._current_mct: Optional[Mct] = None
        self._current_footpath: Optional[Footpath] = None

        self._path_2_branch_handler: Dict[str, Callable] = {
            "2_ALS": self._handle_stop,
            "2_ALS/4_PRD": self._handle_mct,
            "2_ALS/5_RFR": self._handle_footpath,
        }

        self._path_2_leaf_handler: Dict[str, Callable] = {
            "ORG": self._handle_org,
            "HDR": self._handle_hdr,
            "2_ALS/ALS": self._handle_2_als,
            "2_ALS/POP": self._handle_2_pop,
            "2_ALS/CNY": self._handle_2_cny,
            "2_ALS/TIZ": self._handle_2_tiz,
            "2_ALS/IFT": self._handle_2_ift,
            "2_ALS/4_PRD/PRD": self._handle_2_4_prd,
            "2_ALS/5_RFR/RFR": self._handle_2_5_rfr,
            "2_ALS/5_RFR/MES": self._handle_2_5_mes,
            "2_ALS/5_RFR/RLS": self._handle_2_5_rls,
            "2_ALS/5_RFR/6_PRD/PRD": self._handle_2_5_6_prd,
            "2_ALS/5_RFR/6_PRD/SER": self._handle_2_5_6_ser,
        }

        # Check if the paths in self._path_2_branch_handler and self._path_2_leaf_handler are spelled correctly.
        if definition:
            all_paths = []
            for top_node in definition.structure.child_list:
                all_paths.extend(
                    self._make_all_paths(
                        node=top_node,
                        is_top_node=True,
                        parent_path="",
                    ))

            invalid_paths = self._path_2_branch_handler.keys() - all_paths
            if invalid_paths:
                raise MeritsException(
                    f'Invalid branch paths: {list(invalid_paths)}.'
                )
            invalid_paths = self._path_2_leaf_handler.keys() - all_paths
            if invalid_paths:
                raise MeritsException(
                    f'Invalid leaf paths: {list(invalid_paths)}.'
                )

    @staticmethod
    def _make_all_paths(
            node: Node,
            is_top_node: bool,
            parent_path: str,
            separator: str = "/",
    ) -> List[str]:
        """
        This method recursively makes all paths that are defined in the structure.
        :param node:
        :param is_top_node:
        :param parent_path:
        :param separator:
        :return:
        """
        if is_top_node:
            node_path = node.name
        else:
            node_path = parent_path + separator + node.name
        result = [node_path]
        if node.child_list:
            for child_node in node.child_list:
                result.extend(
                    DataHandlerToCsvCollector._make_all_paths(
                        node=child_node,
                        is_top_node=False,
                        parent_path=node_path,
                        separator=separator,
                    ))
        return result

    def get_csv_file_name_2_next_id(self) -> Dict[str, int]:
        """
        Gives the next row ID's for the CSV files. The ID's will be one more than the last one used in the current CSV
        files.
        :return:
        """
        return {
            STOP_FILE_NAME: self._next_stop_id,
            SYNONYM_FILE_NAME: self._next_synonym_id,
            MCT_FILE_NAME: self._next_mct_id,
            FOOTPATH_FILE_NAME: self._next_footpath_id,
        }

    def set_csv_file_name_2_next_id(
            self,
            csv_file_name_2_next_id: Dict[str, int],
    ):
        """
        Sets the initial/next row ID's for the CSV files
        :param csv_file_name_2_next_id:
        :return:
        """
        self._next_stop_id = csv_file_name_2_next_id.get(STOP_FILE_NAME, self._next_stop_id)
        self._next_synonym_id = csv_file_name_2_next_id.get(SYNONYM_FILE_NAME, self._next_synonym_id)
        self._next_mct_id = csv_file_name_2_next_id.get(MCT_FILE_NAME, self._next_mct_id)
        self._next_footpath_id = csv_file_name_2_next_id.get(FOOTPATH_FILE_NAME, self._next_footpath_id)

    def on_enter_branch(self, branch: DataBranch) -> None:
        handler = self._path_2_branch_handler.get(branch.path)
        if handler:
            handler(begin=True)

    def on_exit_branch(self, path: str) -> None:
        handler = self._path_2_branch_handler.get(path)
        if handler:
            handler(begin=False)

    def on_enter_leaf(self, leaf: DataLeaf):
        handler = self._path_2_leaf_handler.get(leaf.path)
        if handler:
            handler(leaf=leaf, begin=True)

    def on_exit_leaf(self, path: str):
        handler = self._path_2_leaf_handler.get(path)
        if handler:
            handler(leaf=None, begin=False)

    def _handle_stop(self, begin: bool):
        if begin:
            self._current_stop = Stop(self._next_stop_id)
            self._next_stop_id += 1
        else:
            self._csv_collector.collect(
                csv_file_name=STOP_FILE_NAME,
                row=dataclasses.asdict(self._current_stop),
            )
            self._current_stop = None

    def _handle_mct(self, begin: bool):
        if begin:
            self._current_mct = Mct(
                mct_id=self._next_mct_id,
                stop_id=self._current_stop.stop_id,
            )
            self._next_mct_id += 1
        else:
            self._csv_collector.collect(
                csv_file_name=MCT_FILE_NAME,
                row=dataclasses.asdict(self._current_mct),
            )
            self._current_mct = None

    def _handle_footpath(self, begin: bool):
        if begin:
            # Skip, because Footpath will be created in _handle_2_5_rfr only if code is AWN.
            pass
        else:
            if self._current_footpath is not None:
                self._csv_collector.collect(
                    csv_file_name=FOOTPATH_FILE_NAME,
                    row=dataclasses.asdict(self._current_footpath),
                )
                self._current_footpath = None

    def _handle_org(self, leaf: DataLeaf, begin: bool):
        if begin:
            self._meta = Meta()
            obj = self._meta
            obj.originator = leaf.get("message_provider")

    def _handle_hdr(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._meta
            validity_first_date, _, validity_last_date = leaf.get("validity").partition("/")
            obj.validity_first_date = validity_first_date
            obj.validity_last_date = validity_last_date
            obj.reference = leaf.get("reference_number")
            self._csv_collector.collect(
                csv_file_name=META_FILE_NAME,
                row=dataclasses.asdict(obj),
            )

    def _handle_2_als(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_stop
            obj.function_code = leaf.get("location_function_code")
            obj.uic_code = leaf.get("uic_code")
            obj.location_name = leaf.get("location_name")
            obj.latitude = leaf.get("latitude")
            obj.longitude = leaf.get("longitude")

    def _handle_2_pop(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_stop
            qualifier = leaf.get("period_qualifier")
            if qualifier == "273":
                first_day, _, last_day = leaf.get("first_day_last_day").partition("/")
                obj.valid_from = first_day
                obj.valid_to = last_day
            elif qualifier == "87":
                obj.default_transfer_time = leaf.get("first_day_last_day")
            else:
                raise MeritsException(
                    f'Unsupported period_qualifier "{qualifier}" at {leaf.path}.'
                )

    def _handle_2_cny(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_stop
            obj.country = leaf.get("country_code")

    def _handle_2_tiz(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_stop
            obj.timezone_1 = leaf.get("time_zone")
            obj.timezone_2 = leaf.get("time_variation")

    def _handle_2_ift(self, leaf: DataLeaf, begin: bool):
        if begin:
            code = leaf.get("text_subject_code")
            if code == "AGW":
                self._current_synonym = Synonym(
                    synonym_id=self._next_synonym_id,
                    stop_id=self._current_stop.stop_id,
                )
                self._next_synonym_id += 1
                obj = self._current_synonym
                obj.uic_code = self._current_stop.uic_code
                obj.language = leaf.get("language_code")
                obj.synonym = leaf.get("location_name")
                self._csv_collector.collect(
                    SYNONYM_FILE_NAME,
                    dataclasses.asdict(self._current_synonym),
                )
                self._current_synonym = None
            elif code == "X02":
                obj = self._current_stop
                obj.location_short_name = leaf.get("location_name")

    def _handle_2_4_prd(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_mct
            obj.uic_code = self._current_stop.uic_code
            obj.service_brand_1 = leaf.get("service_mode_or_brand_1")
            obj.service_brand_2 = leaf.get("service_mode_or_brand_2")
            obj.time = leaf.get("mct")
            obj.service_provider_1 = leaf.get("service_provider_1")
            obj.service_provider_2 = leaf.get("service_provider_2")

    def _handle_2_5_rfr(self, leaf: DataLeaf, begin: bool):
        if begin:
            code = leaf.get("reference_function_code")
            if code == "X01":
                obj = self._current_stop
                obj.reservation_code = leaf.get("uic_code")
            elif code == "AWN":
                # Create Footpath
                self._current_footpath = Footpath(
                    footpath_id=self._next_footpath_id,
                    stop_id=self._current_stop.stop_id,
                )
                self._next_footpath_id += 1
                obj = self._current_footpath
                obj.uic_code_1 = self._current_stop.uic_code
                obj.uic_code_2 = leaf.get("uic_code")

    def _handle_2_5_mes(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_footpath
            obj.duration = leaf.get("transfer_time")
            obj.duration_unit = leaf.get("unit")

    def _handle_2_5_rls(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_footpath
            obj.relationship_code_13 = leaf.get("relation_type_code")
            obj.footpath_6_or_hierarchy_14 = leaf.get("relation")

    def _handle_2_5_6_prd(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_footpath
            obj.service_brand_1 = leaf.get("service_mode_or_brand_1")
            obj.service_brand_2 = leaf.get("service_mode_or_brand_2")
            obj.service_provider_1 = leaf.get("service_provider_1")
            obj.service_provider_2 = leaf.get("service_provider_2")

    def _handle_2_5_6_ser(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_footpath
            if obj.attributes_with_semicolon is None:
                obj.attributes_with_semicolon = ""
            obj.attributes_with_semicolon += leaf.get("ser_code") + ";"
