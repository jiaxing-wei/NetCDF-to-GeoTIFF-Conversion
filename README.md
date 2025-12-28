# NetCDF to GeoTIFF Conversion for Daily Evapotranspiration

This repository provides a Python-based workflow for converting yearly NetCDF evapotranspiration (ET) datasets into daily GeoTIFF files. The implementation is designed for geospatial raster time series and preserves spatial reference, resolution, and temporal information.

---

## Overview

The script reads a yearly NetCDF file containing daily evapotranspiration data stacked along a time dimension and exports each time slice as an individual GeoTIFF file. The output GeoTIFF filenames are generated using the year and day-of-year (DOY), enabling seamless reconstruction of daily raster products.

Temporal information is taken directly from the `time` variable in the NetCDF file, allowing for non-continuous or irregular DOY sequences.

---

## Input Data

### NetCDF File

The input NetCDF file must contain at least the following variables and attributes:

- `ET (time, lat, lon)`  
  Daily evapotranspiration values
- `lat (lat)`  
  Latitude coordinates (pixel centers)
- `lon (lon)`  
  Longitude coordinates (pixel centers)
- `time (time)`  
  Day of year (DOY), stored explicitly
- `crs` (optional but recommended)  
  Coordinate reference system information (`spatial_ref`, WKT)

A global attribute is expected:
- `year` — four-digit year of the dataset

---

## Output Data

### GeoTIFF Files

One GeoTIFF file is generated per time step:
