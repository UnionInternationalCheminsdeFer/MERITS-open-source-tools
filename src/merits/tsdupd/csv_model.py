"""
This module contains classes that each represent one row in a TSDUPD CSV file.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Stop:
    stop_id: int
    function_code: Optional[str] = None
    uic_code: Optional[str] = None
    location_name: Optional[str] = None
    location_short_name: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    default_transfer_time: Optional[str] = None
    country: Optional[str] = None
    timezone_1: Optional[str] = None
    timezone_2: Optional[str] = None
    reservation_code: Optional[str] = None


@dataclass
class Synonym:
    synonym_id: int
    stop_id: int
    uic_code: Optional[str] = None
    language: Optional[str] = None
    synonym: Optional[str] = None


@dataclass
class Mct:
    mct_id: int
    stop_id: int
    uic_code: Optional[str] = None
    service_brand_1: Optional[str] = None
    service_brand_2: Optional[str] = None
    time: Optional[str] = None
    service_provider_1: Optional[str] = None
    service_provider_2: Optional[str] = None


@dataclass
class Footpath:
    footpath_id: int
    stop_id: int
    uic_code_1: Optional[str] = None
    uic_code_2: Optional[str] = None
    duration: Optional[str] = None
    duration_unit: Optional[str] = None
    relationship_code_13: Optional[str] = None
    footpath_6_or_hierarchy_14: Optional[str] = None
    attributes_with_semicolon: Optional[str] = None
    service_brand_1: Optional[str] = None
    service_brand_2: Optional[str] = None
    service_provider_1: Optional[str] = None
    service_provider_2: Optional[str] = None


@dataclass
class Meta:
    reference: Optional[str] = None
    "The reference is the time of conversion as a string of format '%Y-%m-%dT%H%M%S'."
    validity_first_date: Optional[str] = None
    "The first date (inclusive) of validity in format '%Y-%m-%d'."
    validity_last_date: Optional[str] = None
    "The last date (inclusive) of validity in format '%Y-%m-%d'."
    originator: Optional[str] = None
