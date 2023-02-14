from typing import Dict, List, Optional

from merits.csvs_zip.csv_handler import CsvHandler
from merits.edifact.collector import Collector
from merits.edifact.definition_model import Definition
from merits.edifact.edifact_writer import EdifactWriter
from merits.exceptions import MeritsException
from merits.tsdupd.csv_model import Stop, Synonym, Mct, Footpath, Meta
from merits.tsdupd.definition import (
    STOP_FILE_NAME, SYNONYM_FILE_NAME, MCT_FILE_NAME, FOOTPATH_FILE_NAME
)


class CsvHandlerToEdifactCollector(CsvHandler):
    """
    This class contains the mapping from TSDUPD CSV's to EDIFACT. From the code it should be clear what happens.
    """

    def __init__(
            self,
            edifact_collector: Collector,
            definition: Definition,
    ):
        """

        :param edifact_collector:
        :param definition:
        """
        super().__init__()

        self.edifact_collector = edifact_collector
        self.definition = definition
        self._edifact_writer = EdifactWriter(self.definition)

        self._current_stop: Optional[Stop] = None
        """
        The current/last stop is needed, at least for the reservation_code, because this needs to be added AFTER it's
        MCT children.
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
                "location_provider": meta.originator,
            }
        )
        # Add new HDR
        if meta.validity_last_date:
            validity = f"{meta.validity_first_date}/{meta.validity_last_date}"
        else:
            validity = meta.validity_first_date
        self._write(
            path="HDR",
            data={
                "validity": validity,
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
        if csv_file_name == STOP_FILE_NAME:
            obj = Stop(**row)
            self._handle_stop(obj)
        elif csv_file_name == SYNONYM_FILE_NAME:
            obj = Synonym(**row)
            self._handle_synonym(obj)
        elif csv_file_name == MCT_FILE_NAME:
            obj = Mct(**row)
            self._handle_mct(obj)
        elif csv_file_name == FOOTPATH_FILE_NAME:
            obj = Footpath(**row)
            self._handle_footpath(obj)
        else:
            raise MeritsException(
                f'Unknown csv_file_name: "{csv_file_name}".'
            )

    def handle_end(self, meta_data: Dict[str, str]):
        self._handle_stop_end()
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

    def _handle_stop(self, obj: Stop):
        self._handle_stop_end()
        self._current_stop = obj
        # Add new 2_ALS/ALS
        self._write(
            path="2_ALS/ALS",
            data={
                "location_function_code": obj.function_code,
                "uic_code": obj.uic_code,
                "location_name": obj.location_name,
                "latitude": obj.latitude,
                "longitude": obj.longitude,
            },
        )
        # Add new 2_ALS/POP+273
        if obj.valid_from or obj.valid_to:
            if obj.valid_to:
                first_day_last_day = obj.valid_from + "/" + obj.valid_to
            else:
                first_day_last_day = obj.valid_from
            self._write(
                path="2_ALS/POP",
                data={
                    "period_qualifier": "273",
                    "first_day_last_day": first_day_last_day,
                },
            )
        # Add new 2_ALS/POP+87
        if obj.default_transfer_time:
            self._write(
                path="2_ALS/POP",
                data={
                    "period_qualifier": "87",
                    "first_day_last_day": obj.default_transfer_time,
                },
            )
        # Add new 2_ALS/CNY
        if obj.country:
            self._write(
                path="2_ALS/CNY",
                data={
                    "country_code": obj.country,
                },
            )
        # Add new 2_ALS/TIZ
        if obj.timezone_1:
            self._write(
                path="2_ALS/TIZ",
                data={
                    "time_zone": obj.timezone_1,
                    "time_variation": obj.timezone_2,
                },
            )
        # Add new 2_ALS/IFT+X02
        if obj.location_short_name:
            self._write(
                path="2_ALS/IFT",
                data={
                    "text_subject_code": "X02",
                    "location_name": obj.location_short_name,
                },
            )

    def _handle_synonym(self, obj: Synonym):
        # Add new 2_ALS/IFT+AGW
        self._write(
            path="2_ALS/IFT",
            data={
                "text_subject_code": "AGW",
                "language_code": obj.language,
                "location_name": obj.synonym,
            },
        )

    def _handle_mct(self, obj: Mct):
        # Add new 2_ALS/4_PRD/PRD
        self._write(
            path="2_ALS/4_PRD/PRD",
            data={
                "service_mode_or_brand_1": obj.service_brand_1,
                "service_mode_or_brand_2": obj.service_brand_2,
                "mct": obj.time,
                "service_provider_1": obj.service_provider_1,
                "service_provider_2": obj.service_provider_2,
            },
        )

    def _handle_stop_end(self):
        """
        This method handles RFR+X01 which relates to TSDUPD_STOP.csv but comes after the last Mct child. It will add
        the RFR+X01 if there is data, then it will make the self._current_stop None. This way the method can be called
        repeatedly from each point where it might be relevant.
        :return:
        """
        # Add new 2_ALS/5_RFR/RFR+X01
        if self._current_stop and self._current_stop.reservation_code:
            self._write(
                path="2_ALS/5_RFR/RFR",
                data={
                    "reference_function_code": "X01",
                    "uic_code": self._current_stop.reservation_code,
                },
            )
        self._current_stop = None

    def _handle_footpath(self, obj: Footpath):
        self._handle_stop_end()
        # Add new 2_ALS/5_RFR/RFR+AWN
        self._write(
            path="2_ALS/5_RFR/RFR",
            data={
                "reference_function_code": "AWN",
                "uic_code": obj.uic_code_2,
            },
        )
        # Add new 2_ALS/5_RFR/MES
        if obj.duration:
            self._write(
                path="2_ALS/5_RFR/MES",
                data={
                    "transfer_time": obj.duration,
                    "unit": obj.duration_unit,
                },
            )
        # ADD new 2_ALS/5_RFR/RLS
        if obj.relationship_code_13:
            self._write(
                path="2_ALS/5_RFR/RLS",
                data={
                    "relation_type_code": obj.relationship_code_13,
                    "relation": obj.footpath_6_or_hierarchy_14,
                },
            )
        # Add new 2_ALS/5_RFR/6_PRD/PRD
        if (
                # Add to indicate group 2_ALS/5_RFR/6_PRD for 2_ALS/5_RFR/6_PRD/SER below.
                obj.attributes_with_semicolon
                # Add for regular data
                or obj.service_brand_1 or obj.service_provider_1
                or obj.service_brand_2 or obj.service_provider_2
        ):
            self._write(
                path="2_ALS/5_RFR/6_PRD/PRD",
                data={
                    "service_mode_or_brand_1": obj.service_brand_1,
                    "service_mode_or_brand_2": obj.service_brand_2,
                    "service_provider_1": obj.service_provider_1,
                    "service_provider_2": obj.service_provider_2,
                },
            )
        # Add new 2_ALS/5_RFR/6_PRD/SER for each attribute
        if obj.attributes_with_semicolon:
            attributes = obj.attributes_with_semicolon.split(";")
            if attributes and not attributes[-1]:
                attributes = attributes[:-1]
            for attribute in attributes:
                self._write(
                    path="2_ALS/5_RFR/6_PRD/SER",
                    data={
                        "ser_code": attribute,
                    },
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
