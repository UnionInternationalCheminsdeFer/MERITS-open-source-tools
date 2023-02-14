"""
This module contains classes that each represent one row in a SKDUPD CSV file.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Relation:
    relation_id: int
    por_id: int
    train_id: int
    service: Optional[str] = None
    relation: Optional[str] = None
    transfer_time: Optional[str] = None
    certainty: Optional[str] = None


@dataclass
class Por:
    por_id: int
    train_id: int
    stop_number: int
    uic: Optional[str] = None
    arrival_time: Optional[str] = None
    arrival_time_offset: Optional[str] = None
    departure_time: Optional[str] = None
    departure_time_offset: Optional[str] = None
    arrival_platform: Optional[str] = None
    departure_platform: Optional[str] = None
    property: Optional[str] = None
    traffic_restriction_code: Optional[str] = None
    distance_and_unit: Optional[str] = None
    "Distance and unit of distance."
    loading_vehicles: Optional[str] = None
    unloading_vehicles: Optional[str] = None
    check_out: Optional[str] = None
    check_in: Optional[str] = None


@dataclass
class Odi:
    odi_id: int
    train_id: int
    from_stop_number: Optional[str] = None
    to_stop_number: Optional[str] = None
    tff_or_asd_or_ser: Optional[str] = None
    reservation: Optional[str] = None
    equipment: Optional[str] = None
    tariff_or_quantity: Optional[str] = None


@dataclass
class Train:
    train_id: int
    service_number: Optional[str] = None
    reservation: Optional[str] = None
    tariff: Optional[str] = None
    service_mode: Optional[str] = None
    service_name: Optional[str] = None
    service_provider: Optional[str] = None
    information_provider: Optional[str] = None  # = "not used in MERITS"
    reservation_company: Optional[str] = None
    first_day: Optional[str] = None
    last_day: Optional[str] = None
    operation_days: Optional[str] = None
    second_service_number: Optional[str] = None


@dataclass
class Meta:
    reference: Optional[str] = None
    "The reference is the time of conversion as a string of format '%Y-%m-%dT%H%M%S'."
    validity_first_date: Optional[str] = None
    "The first date (inclusive) of validity in format '%Y-%m-%d'."
    validity_last_date: Optional[str] = None
    "The last date (inclusive) of validity in format '%Y-%m-%d'."
    originator: Optional[str] = None
