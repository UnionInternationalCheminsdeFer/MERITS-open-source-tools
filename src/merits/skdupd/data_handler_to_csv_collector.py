import dataclasses
from copy import deepcopy
from typing import Optional, Callable, Dict, List

from merits.csvs_zip.collector import Collector
from merits.edifact.data_handler import DataHandler
from merits.edifact.definition_model import Definition, Node
from merits.edifact.object_model import DataLeaf, DataBranch
from merits.exceptions import MeritsException
from merits.skdupd.csv_model import Train, Por, Relation, Odi, Meta
from merits.skdupd.definition import META_FILE_NAME, ODI_FILE_NAME, RELATION_FILE_NAME, POR_FILE_NAME, TRAIN_FILE_NAME


class DataHandlerToCsvCollector(DataHandler):
    """
    This class contains the mapping from SKDUPD EDIFACT to CSV files. From the code it should be clear what happens.

    This conversion has SKDUPD_TRAIN.csv as the root table which is related to the 2_PRD/4_POP node. On the EDIFACT side
    group 2_PRD is the parent but there is no CSV table related to this. Instead, information at the 2_PRD level is
    repeated in every SKDUPD_TRAIN.csv row. The repeatable data is stored in self._current_train_service.
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
        self._next_train_id = 1
        self._next_stop_number = -1
        "The Por.stop_number resets to 1 for every next train. Por.por_id continues."
        self._next_por_id = 1
        self._next_relation_id = 1
        self._next_odi_id = 1
        self._meta: Optional[Meta] = None
        self._current_train_service: Optional[Train] = None
        self._current_train: Optional[Train] = None
        self._current_por: Optional[Por] = None
        self._current_relation: Optional[Relation] = None
        self._current_odi: Optional[Odi] = None

        self._path_2_branch_handler: Dict[str, Callable] = {
            "2_PRD": self._handle_train_service,
            "2_PRD/4_POP": self._handle_train,
            "2_PRD/4_POP/7_POR": self._handle_por,
            "2_PRD/4_POP/7_POR/8_RFR": self._handle_relation,
            "2_PRD/4_POP/9_ODI": self._handle_odi,
        }

        self._path_2_leaf_handler: Dict[str, Callable] = {
            "ORG": self._handle_org,
            "HDR": self._handle_hdr,
            "2_PRD/PRD": self._handle_2_prd,
            "2_PRD/RFR": self._handle_2_rfr,
            "2_PRD/4_POP/POP": self._handle_2_4_pop,
            "2_PRD/4_POP/7_POR/POR": self._handle_2_4_7_por,
            "2_PRD/4_POP/7_POR/MES": self._handle_2_4_7_mes,
            "2_PRD/4_POP/7_POR/ASD": self._handle_2_4_7_asd,
            "2_PRD/4_POP/7_POR/TRF": self._handle_2_4_7_trf,
            "2_PRD/4_POP/7_POR/8_RFR/RFR": self._handle_2_4_7_8_rfr,
            "2_PRD/4_POP/7_POR/8_RFR/RLS": self._handle_2_4_7_8_rls,
            "2_PRD/4_POP/7_POR/8_RFR/TCE": self._handle_2_4_7_8_tce,
            "2_PRD/4_POP/9_ODI/ODI": self._handle_2_4_9_odi,
            "2_PRD/4_POP/9_ODI/PDT": self._handle_2_4_9_pdt,
            "2_PRD/4_POP/9_ODI/TFF": self._handle_2_4_9_tff,
            "2_PRD/4_POP/9_ODI/ASD": self._handle_2_4_9_asd,
            "2_PRD/4_POP/9_ODI/10_SER/SER": self._handle_2_4_9_10_ser,
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
            TRAIN_FILE_NAME: self._next_train_id,
            POR_FILE_NAME: self._next_por_id,
            RELATION_FILE_NAME: self._next_relation_id,
            ODI_FILE_NAME: self._next_odi_id,
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
        self._next_train_id = csv_file_name_2_next_id.get(TRAIN_FILE_NAME, self._next_train_id)
        self._next_por_id = csv_file_name_2_next_id.get(POR_FILE_NAME, self._next_por_id)
        self._next_relation_id = csv_file_name_2_next_id.get(RELATION_FILE_NAME, self._next_relation_id)
        self._next_odi_id = csv_file_name_2_next_id.get(ODI_FILE_NAME, self._next_odi_id)

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

    def _handle_train_service(self, begin: bool):
        if begin:
            self._current_train_service = Train(train_id=-1)
        else:
            self._current_train_service = None

    def _handle_train(self, begin: bool):
        if begin:
            self._current_train = deepcopy(self._current_train_service)
            self._current_train.train_id = self._next_train_id
            self._next_train_id += 1
            self._next_stop_number = 1
        else:
            self._csv_collector.collect(
                csv_file_name=TRAIN_FILE_NAME,
                row=dataclasses.asdict(self._current_train),
            )
            self._current_train = None

    def _handle_por(self, begin: bool):
        if begin:
            self._current_por = Por(
                train_id=self._current_train.train_id,
                por_id=self._next_por_id,
                stop_number=self._next_stop_number,
            )
            self._next_por_id += 1
            self._next_stop_number += 1
        else:
            self._csv_collector.collect(
                csv_file_name=POR_FILE_NAME,
                row=dataclasses.asdict(self._current_por),
            )
            self._current_por = None

    def _handle_relation(self, begin: bool):
        if begin:
            self._current_relation = Relation(
                train_id=self._current_por.train_id,
                por_id=self._current_por.por_id,
                relation_id=self._next_relation_id,
            )
            self._next_relation_id += 1
        else:
            self._csv_collector.collect(
                csv_file_name=RELATION_FILE_NAME,
                row=dataclasses.asdict(self._current_relation),
            )
            self._current_relation = None

    def _handle_odi(self, begin: bool):
        if begin:
            self._current_odi = Odi(
                train_id=self._current_train.train_id,
                odi_id=self._next_odi_id,
            )
            self._next_odi_id += 1
        else:
            self._csv_collector.collect(
                csv_file_name=ODI_FILE_NAME,
                row=dataclasses.asdict(self._current_odi),
            )
            self._current_odi = None

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

    def _handle_2_prd(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_train_service
            obj.service_number = leaf.get("service_number")
            obj.reservation = leaf.get("reservation")
            obj.tariff = leaf.get("tariff")
            obj.service_mode = leaf.get("service_mode")
            obj.service_name = leaf.get("service_name")
            obj.service_provider = leaf.get("service_provider")
            obj.reservation_company = leaf.get("reservation_company")

    def _handle_2_rfr(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_train_service
            obj.second_service_number = leaf.get("second_service_number")

    def _handle_2_4_pop(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_train
            period = leaf.get("first_day_last_day")
            if period:
                first_day, _, last_day = period.partition("/")
            else:
                first_day, last_day = None, None
            obj.first_day = first_day
            obj.last_day = last_day
            obj.operation_days = leaf.get("days")

    def _handle_2_4_7_por(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_por
            obj.uic = leaf.get("uic")
            obj.arrival_time = leaf.get("arrival")
            obj.arrival_time_offset = leaf.get("arrival_offset")
            obj.departure_time = leaf.get("departure")
            obj.departure_time_offset = leaf.get("departure_offset")
            obj.arrival_platform = leaf.get("arrival_platform")
            obj.departure_platform = leaf.get("departure_platform")
            obj.property = leaf.get("location_qualifier")

    def _handle_2_4_7_mes(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_por
            obj.distance_and_unit = leaf.get("distance") + ":" + leaf.get("unit")

    def _handle_2_4_7_asd(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_por
            asd_code = leaf.get("asd_code")
            if asd_code == "7":
                obj.loading_vehicles = "ASD+7"
            elif asd_code == "9":
                obj.unloading_vehicles = "ASD+9"
            elif asd_code == "44":
                obj.check_out = leaf.get("last_time")
            elif asd_code == "45":
                obj.check_in = leaf.get("first_time")

    def _handle_2_4_7_trf(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_por
            obj.traffic_restriction_code = leaf.get("trf_code")

    def _handle_2_4_7_8_rfr(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_relation
            obj.service = leaf.get("service_number")

    def _handle_2_4_7_8_rls(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_relation
            obj.relation = leaf.get("relation")

    def _handle_2_4_7_8_tce(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_relation
            obj.transfer_time = leaf.get("transfer_time")
            obj.certainty = leaf.get("certainty")

    def _handle_2_4_9_odi(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_odi
            obj.from_stop_number = leaf.get("from_stop_number")
            obj.to_stop_number = leaf.get("to_stop_number")

    def _handle_2_4_9_pdt(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_odi
            obj.reservation = leaf.get("reservation")
            obj.equipment = leaf.get("brand_code")
            obj.tariff_or_quantity = leaf.get("tariff")

    def _handle_2_4_9_tff(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_odi
            # A prefix for tff_or_asd_or_ser is found in the ReferenceData_20230104.xls by the first tag-2 ID found in
            # the Leaflet.
            obj.tff_or_asd_or_ser = "P" + leaf.get("tff_code")

    def _handle_2_4_9_asd(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_odi
            # A prefix for tff_or_asd_or_ser is found in the ReferenceData_20230104.xls by the first tag-2 ID found in
            # the Leaflet.
            obj.tff_or_asd_or_ser = "S" + leaf.get("asd_code")
            obj.reservation = leaf.get("reservation")

    def _handle_2_4_9_10_ser(self, leaf: DataLeaf, begin: bool):
        if begin:
            obj = self._current_odi
            # A prefix for tff_or_asd_or_ser is found in the ReferenceData_20230104.xls by the first tag-2 ID found in
            # the Leaflet.
            obj.tff_or_asd_or_ser = "F" + leaf.get("ser_code")
            obj.reservation = leaf.get("reservation")
            obj.tariff_or_quantity = leaf.get("units_quantity")
