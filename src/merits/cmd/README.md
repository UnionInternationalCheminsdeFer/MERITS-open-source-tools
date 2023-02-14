# MERITS Conversion Command Line Tool

A command line tool is provided that wraps the MERITS Conversion library.

The tool has eight operations:

- for SKDPD or STDUPD
- from CSV to EDIFACT or the other way around
- one or multiple EDIFACT files

After installation of the library an executable `merits-convert` becomes available. The only required argument is the
conversion type, which selects the operation. For convenience for each operation another executable is provided that
has only optional arguments. These executables are:

`skdupd2csv`
`csv2skdupd`
`tsdupd2csv`
`csv2tsdupd`
`skdupd2csvmulti`
`csv2skdupdmulti`
`tsdupd2csvmulti`
`csv2tsdupdmulti`

Without further arguments these work on the current directory and default file names (see below).

## Arguments

- conversion: (only for `merits-convert`) Selects the conversion. One of
  `skdupd-csv-edifact`
  `skdupd-edifact-csv`
  `tsdupd-csv-edifact`
  `tsdupd-edifact-csv`
  `skdupd-csv-edifact-multi`
  `skdupd-edifact-csv-multi`
  `tsdupd-csv-edifact-multi`
  `tsdupd-edifact-csv-multi`
- `--input` `-i`: (optional) Selects the input. See the chapter below for expected and default values.
- `--output` `-o`: (optional) Selects the output. See the chapter below for expected and default values.
- `--csv-zip`: (boolean flag) If present, the CSV files related to one EDIFACT file will be in one ZIP file. This works
  for both input and output.
- `--csv-id`: (optional) Sets initial row ID's for CSV tables created by the conversion. For
  example `--csv-id SKDUPD_TRAIN.csv=12 SKDUPD_POR.csv=3456`. When using an EDIFACT to CSVs **multi** conversion, the
  row ID's will count on over all CSV files with the same name. This makes import into a database easier.

## Input and Output

The table below gives an overview of what is expected as input or output and what the defaults are.

Where `*.csv` files are mentioned, the default names for the chosen conversion are meant. For SKDUPD these are
`meta.csv`
`SKDUPD_ODI.csv`
`SKDUPD_RELATION.csv`
`SKDUPD_POR.csv`
`SKDUPD_TRAIN.csv`
`SKDUPD.zip`.
For TSDUPD the files are
`meta.csv`
`TSDUPD_STOP.csv`
`TSDUPD_SYNONYM.csv`
`TSDUPD_MCT.csv`
`TSDUPD_FOOTPATH.csv`
`TSDUPD.zip`

Where `*.zip` is mentioned the CSV files inside the ZIP file will have the default names for the chosen conversion.

With multi-conversions the outputs will be named like the related input but with different extensions `.r`, `.zip`, and
none for subdirectories.

| Multi            | Direction       | --csv-zip | --input                                                       | --output                                                    | Default Input                    | Default Output                   |
|------------------|-----------------|-----------|---------------------------------------------------------------|-------------------------------------------------------------|----------------------------------|----------------------------------|
| Single EDIFACT   | EDIFACT ==> CSV | No        | existing `*.r` file                                           | directory (`*.csv` will be made)                            | `SKDUPD.r` or `TSDUPD.r`         | work directory                   |
| Single EDIFACT   | EDIFACT ==> CSV | Yes       | existing `*.r` file                                           | new `*.zip` file                                            | `SKDUPD.r` or `TSDUPD.r`         | `./SKDUPD.zip` or `./TSDUPD.zip` |
| Single EDIFACT   | CSV ==> EDIFACT | No        | existing directory with `*.csv` files in it                   | new `*.r` file                                              | work directory                   | `SKDUPD.r` or `TSDUPD.r`         |
| Single EDIFACT   | CSV ==> EDIFACT | Yes       | existing `*.zip` file                                         | new `*.r` file                                              | `./SKDUPD.zip` or `./TSDUPD.zip` | `SKDUPD.r` or `TSDUPD.r`         |
| Multiple EDIFACT | EDIFACT ==> CSV | No        | existing directory with `*.r` files in it                     | directory (sub directories with `*.csv` files will be made) | work directory                   | work directory                   |
| Multiple EDIFACT | EDIFACT ==> CSV | Yes       | existing directory with `*.r` files in it                     | directory (`*.zip` files will be made)                      | work directory                   | work directory                   |
| Multiple EDIFACT | CSV ==> EDIFACT | No        | existing directory where each sub dir contains `*.csv`  files | directory (`*.r` files will be made)                        | work directory                   | work directory                   |
| Multiple EDIFACT | CSV ==> EDIFACT | Yes       | existing directory with `*.zip` files in it                   | directory (`*.r` files will be made)                        | work directory                   | work directory                   |

## Logs

The MERITS Command Line Tool will log to file `merits-convert.log` in the working directory. 
