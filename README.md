# MERITS Transformation Tools

Transformation of both timetable and location data structures between MERITS EDIFACT and CSV in both directions.

This tool is provided as a library and for convenience a command line tool is also provided.

## Requirements

Python 3.9 or newer. (No dependencies on other python packages.)

## Installation

Not yet in PyPi. Please install from source. See below.

## Installation from sources

Download the sources from GitHub. There should be a green `<> Code` button on this page or its parent. This opens a pull
down where you can clone the repo or `Download ZIP`.

Once you have the (unzipped) source on your local disk, open a command prompt that provides python 3.9 or newer. Change
directory to directory that contains this README file. Then run `pip install .`

## Library use

To start quickly, use `merits.skdupd.edifact_to_csv`, `merits.skdupd.csv_to_edifact`, `merits.tsdupd.edifact_to_csv`,
and `merits.tsdupd.csv_to_edifact`. Use one of the `load*` methods to read and convert the data. After this use one of
the `get*` methods to retrieve the conversion result.

The python package `csvs_zip` contains generic code for working with a hierarchy of CSV tables.

Package `edifact` contain generic code for working with EDIFACT.

In packages `skdupd` and `tsdupd` specific code for SKDUPD and TSDUPD can be found. The mappings are in
the `*_handler_to_*_collector.py` files. The `definition.py` (and `csv_model.py`) file contain the specification of the
SKDUPD and TSDUPD formats and their related CSV hierarchies.

### Development of this library

Developers who need to further develop this library should also read [development documentation](./doc/development.md).

## Command Line Tool

A command line tool using the library is provided. See the [detailed documentation](./src/merits/cmd/README.md).

## Extra specifications

This library supports only part of what would be possible with EDIFACT in general or with the SKDUPD or TSDUPD
specifications. This chapter mentions some limitations.

### General

#### No unnecessary separators

The older conversions have some unnecessary separators. For example old code created

`PRD+75438:14:1::::+1186**86'` and new code creates

`PRD+75438:14:1+1186**86'`

The `::::` is not needed, because the following `+` already tells how to interpret the next value. It is also
inconsistent, because not all (needed or not) separators in the segment are present.

You can convert old EDIFACT to CSVs with the current convertor but when converting from CSVs to EDIFACT it will be
cleaned up.

#### An EDIFACT segment name always has three characters

Every EDIFACT segment name has exactly three characters. This is used to get the segment name without parsing the
segment. Python `segment_name = segment[:3]`

#### EDIFACT segments are `\n` separated

EDIFACT allows segments to be only separated by the segment separator character (by default `'`). This library currently
requires a new line `\n` between the segment separator character and the next segment.

#### No dynamic repeat in a segment

EDIFACT allows in a segment a list of variable length on tag-1 level. This is indicated by an element separator `*`.

Dynamic length lists are NOT supported by this application. Fixed length, fixed order repetition is possible. For
example the first occurrence could indicate arrival and the second departure but only in that order. The fields in the
definition will have unique names that reflect this.

#### Ordered CSV rows

Rows in CSV files must be in the same order as the parent rows.

For example: rows in SKDUPD_POR.csv are linked to a parent row in SKDUPD_TRAIN.csv by field train_id. The order of
train_id must be the same in both files. Such a relation also exists between SKDUPD_RELATION.csv and its parent
SKDUPD_POR.csv by por_id.

#### Paths are unique

In theory the structure of an EDIFACT definition might allow siblings to have the same segment name as long as there is
different, mandatory sibling between them.

This library does NOT support siblings with the same name, because paths are used as unique node identifiers. For
example SKDUPD path `2_PRD/4_POP/7_POR/ASD` can only refer to node `0380`.

### SKDUPD

#### One-on-one relation ODI - (PDT, TFF, ASD, or SER)

There can be only one of

`2_PRD/4_POP/9_ODI/PDT`,

`2_PRD/4_POP/9_ODI/TFF`,

`2_PRD/4_POP/9_ODI/ASD` and

`2_PRD/4_POP/9_ODI/10_SER/SER`

in a

`2_PRD/4_POP/9_ODI/`

This way one row in SKDUPD_ODI.csv relates to one occurrence of the `2_PRD/4_POP/9_ODI/` group in EDIFACT.

The definition and the leaflet allow more but this will not be encountered in practice and will not be supported.

### TSDUPD

#### One-on-one relation 2_ALS/5_RFR to 2_ALS/5_RFR/6_PRD

There can be only one

`2_ALS/5_RFR/6_PRD`

in a

`2_ALS/5_RFR`

This way one row in TSDUPD_FOOTPATH.csv relates to one occurrence of `2_ALS/5_RFR/RFR`
with `reference_function_code` = "AWN".
