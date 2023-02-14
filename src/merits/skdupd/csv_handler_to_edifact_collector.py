from typing import Dict, List, Optional

from merits.csvs_zip.csv_handler import CsvHandler
from merits.edifact.collector import Collector
from merits.edifact.definition_model import Definition
from merits.edifact.edifact_writer import EdifactWriter
from merits.skdupd.csv_model import Train, Por, Relation, Odi, Meta
from merits.skdupd.definition import ODI_FILE_NAME, RELATION_FILE_NAME, POR_FILE_NAME, TRAIN_FILE_NAME


class CsvHandlerToEdifactCollector(CsvHandler):
    """
    This class contains the mapping from SKDUPD CSV's to EDIFACT. From the code it should be clear what happens.
    """

    def __init__(
            self,
            edifact_collector: Collector,
            definition: Definition,
            prd_for_every_pop: bool = True,
    ):
        """

        :param edifact_collector:
        :param definition:
        :param prd_for_every_pop: iff False a 2_PRD/PRD segment will only be added when the Train.service_number differs
            from the previous Train.service_number.
        """
        super().__init__()

        self.edifact_collector = edifact_collector
        self.definition = definition
        self.prd_for_every_pop = prd_for_every_pop
        self._edifact_writer = EdifactWriter(self.definition)

        self._last_service_number: Optional[str] = None
        self._por_list: List[Por] = []
        """
        The Por objects are remembered for the last Train/POP, because Por.uic is needed in 2_PRD/4_POP/9_ODI/ODI fields
        from_stop and to_stop. 
        """

    def handle_begin(self, meta_data: Dict[str, str]):
        meta = Meta(**meta_data)
        # Add new UIB
        self._write(
            path="UIB",
            data={
                "initiator": meta.reference,
            },
            add_defaults_for=[
                "syntax_identifier",
                "syntax_version_number",
            ],
        )
        # Add new UIH
        self._write(
            path="UIH",
            data={
                "initiator": meta.reference,
                "sequence_number": "1",
            },
            add_defaults_for=[
                "message_type",
                "message_version",
                "message_release",
            ]
        )
        # Add new MSD
        self._write(
            path="MSD",
            data={},
            add_defaults_for=[
                "business_function_code",
                "message_function_code",
            ]
        )
        # Add new ORG
        self._write(
            path="ORG",
            data={
                "message_provider": meta.originator,
                "timetable_provider": meta.originator,
            }
        )
        # Add new HDR
        self._write(
            path="HDR",
            data={
                "validity": f"{meta.validity_first_date}/{meta.validity_last_date}",
                "qualifier_code_1": "45",
                "date_1": meta.reference[:-2],
                "reference_number": meta.reference,
            },
            add_defaults_for=[
                "status_description_code",
                "validity_code",
            ]
        )

    def handle_row(self, csv_file_name: str, row: Dict[str, str]):
        if csv_file_name == TRAIN_FILE_NAME:
            obj = Train(**row)
            self._handle_train(obj)
        elif csv_file_name == POR_FILE_NAME:
            obj = Por(**row)
            self._handle_por(obj)
        elif csv_file_name == RELATION_FILE_NAME:
            obj = Relation(**row)
            self._handle_relation(obj)
        elif csv_file_name == ODI_FILE_NAME:
            obj = Odi(**row)
            self._handle_odi(obj)

    def handle_end(self, meta_data: Dict[str, str]):
        meta = Meta(**meta_data)
        # Add new UIT
        self._write(
            path="UIT",
            data={
                "message_reference": "1",
                "number_of_segments": str(self.edifact_collector.segment_count()),
            },
        )
        # Add new UIZ
        self._write(
            path="UIZ",
            data={
                "initiator": meta.reference,
                "number_of_messages": "1",
            },
        )

    def _handle_train(self, train: Train):
        self._por_list.clear()
        if self.prd_for_every_pop or train.service_number != self._last_service_number:
            # Add new 2_PRD/PRD
            self._write(
                path="2_PRD/PRD",
                data={
                    "service_number": train.service_number,
                    "reservation": train.reservation,
                    "tariff": train.tariff,
                    "service_mode": train.service_mode,
                    "service_name": train.service_name,
                    "service_provider": train.service_provider,
                    "reservation_company": train.reservation_company,
                },
            )
            # Add new 2_PRD/RFR
            if train.second_service_number:
                self._write(
                    path="2_PRD/RFR",
                    data={
                        "second_service_number": train.second_service_number,
                    },
                    add_defaults_for=[
                        "reference_function_code",
                    ],
                )
            self._last_service_number = train.service_number
        # Add new 2_PRD/4_POP/POP
        self._write(
            path="2_PRD/4_POP/POP",
            data={
                "first_day_last_day": train.first_day + "/" + train.last_day,
                "days": train.operation_days,
            },
            add_defaults_for=[
                "period_qualifier",
            ],
        )

    def _handle_por(self, obj: Por):
        self._por_list.append(obj)
        # Add new 2_PRD/4_POP/7_POR/POR
        self._write(
            path="2_PRD/4_POP/7_POR/POR",
            data={
                "uic": obj.uic,
                "arrival": obj.arrival_time,
                "arrival_offset": obj.arrival_time_offset,
                "departure": obj.departure_time,
                "departure_offset": obj.departure_time_offset,
                "arrival_platform": obj.arrival_platform,
                "departure_platform": obj.departure_platform,
                "location_qualifier": obj.property,
            },
        )
        # Add new 2_PRD/4_POP/7_POR/MES
        if obj.distance_and_unit:
            distance, _, unit = obj.distance_and_unit.partition(":")
            self._write(
                path="2_PRD/4_POP/7_POR/MES",
                data={
                    "distance": distance,
                    "unit": unit,
                },
            )
        # Add (possibly multiple) new 2_PRD/4_POP/7_POR/ASD
        if obj.loading_vehicles == "ASD+7":
            self._write(
                path="2_PRD/4_POP/7_POR/ASD",
                data={
                    "asd_code": "7",
                },
            )
        if obj.unloading_vehicles == "ASD+9":
            self._write(
                path="2_PRD/4_POP/7_POR/ASD",
                data={
                    "asd_code": "9",
                },
            )
        if obj.check_out:
            self._write(
                path="2_PRD/4_POP/7_POR/ASD",
                data={
                    "asd_code": "44",
                    "last_time": obj.check_out,
                },
            )
        if obj.check_in:
            self._write(
                path="2_PRD/4_POP/7_POR/ASD",
                data={
                    "asd_code": "45",
                    "first_time": obj.check_in,
                },
            )
        # Add new 2_PRD/4_POP/7_POR/TRF
        if obj.traffic_restriction_code:
            self._write(
                path="2_PRD/4_POP/7_POR/TRF",
                data={
                    "trf_code": obj.traffic_restriction_code,
                },
            )

    def _handle_relation(self, obj: Relation):
        # Add new 2_PRD/4_POP/7_POR/8_RFR/RFR
        self._write(
            path="2_PRD/4_POP/7_POR/8_RFR/RFR",
            data={
                "service_number": obj.service,
            },
            add_defaults_for=[
                "reference_function_code",
            ],
        )
        # Add new 2_PRD/4_POP/7_POR/8_RFR/RLS
        if obj.relation:
            self._write(
                path="2_PRD/4_POP/7_POR/8_RFR/RLS",
                data={
                    "relation": obj.relation,
                },
                add_defaults_for=[
                    "relation_type_code",
                ],
            )
        # Add new 2_PRD/4_POP/7_POR/8_RFR/TCE
        if obj.transfer_time or obj.certainty:
            self._write(
                path="2_PRD/4_POP/7_POR/8_RFR/TCE",
                data={
                    "transfer_time": obj.transfer_time,
                    "certainty": obj.certainty,
                },
            )
        pass

    def _handle_odi(self, obj: Odi):
        # Add new 2_PRD/4_POP/9_ODI/ODI
        from_por_idx = int(obj.from_stop_number) - 1
        to_por_idx = int(obj.to_stop_number) - 1
        self._write(
            path="2_PRD/4_POP/9_ODI/ODI",
            data={
                "from_stop": self._por_list[from_por_idx].uic,
                "to_stop": self._por_list[to_por_idx].uic,
                "from_stop_number": obj.from_stop_number,
                "to_stop_number": obj.to_stop_number,
            },
        )
        # Add new 2_PRD/4_POP/9_ODI/PDT
        if obj.equipment:
            self._write(
                path="2_PRD/4_POP/9_ODI/PDT",
                data={
                    "reservation": obj.reservation,
                    "brand_code": obj.equipment,
                    "tariff": obj.tariff_or_quantity,
                },
            )
        if obj.tff_or_asd_or_ser:
            prefix = obj.tff_or_asd_or_ser[0]
            code = obj.tff_or_asd_or_ser[1:]
            # Add new 2_PRD/4_POP/9_ODI/TFF
            if prefix == "P":
                self._write(
                    path="2_PRD/4_POP/9_ODI/TFF",
                    data={
                        "tff_code": code,
                    },
                )
            # Add new 2_PRD/4_POP/9_ODI/ASD
            elif prefix == "S":
                self._write(
                    path="2_PRD/4_POP/9_ODI/ASD",
                    data={
                        "asd_code": code,
                        "reservation": obj.reservation,
                    },
                )
            # Add new 2_PRD/4_POP/9_ODI/10_SER/SER
            elif prefix == "F":
                self._write(
                    path="2_PRD/4_POP/9_ODI/10_SER/SER",
                    data={
                        "ser_code": code,
                        "reservation": obj.reservation,
                        "units_quantity": obj.tariff_or_quantity,
                    }
                )

    def _write(
            self,
            path: str,
            data: Dict[str, str],
            add_defaults_for: Optional[List[str]] = None,
    ):
        """
        Writes an EDIFACT segment to the collector.
        :param path: the path in the structure to find the correct segment format
        :param data: field names to values
        :param add_defaults_for: add the default values from the definition in the result
        :return:
        """
        self.edifact_collector.collect(
            self._edifact_writer.to_edifact(
                path=path,
                data=data,
                add_defaults_for=add_defaults_for,
            )
        )
