import os
import numpy as np
from osgeo import gdal
import netCDF4 as nc

# Enable GDAL exceptions for easier debugging
gdal.UseExceptions()

# ============================================================
# Path configuration
# ============================================================
# Input NetCDF file (yearly ET data)
nc_file = r"***"

# Output directory for GeoTIFF files
out_tif_dir = r"***"
os.makedirs(out_tif_dir, exist_ok=True)

# ============================================================
# Open NetCDF dataset
# ============================================================
ds = nc.Dataset(nc_file, "r")

# Read variables
et = ds.variables["ET"]          # ET(time, lat, lon)
time_var = ds.variables["time"]  # Day of year (DOY)
lat = ds.variables["lat"][:]     # Latitude centers
lon = ds.variables["lon"][:]     # Longitude centers

# Get dimensions
ntime, nlat, nlon = et.shape

# Read year attribute (stored as global attribute)
year = int(ds.year)

# ============================================================
# Construct GeoTransform from lat/lon coordinates
# ============================================================
# Assumption:
#   - lat and lon are 1D arrays representing pixel centers
#   - grid is regular and north-up
dx = lon[1] - lon[0]
dy = lat[1] - lat[0]

# Upper-left corner of the upper-left pixel
x0 = lon[0] - dx / 2
y0 = lat[0] - dy / 2

# GDAL GeoTransform: (origin_x, pixel_width, 0, origin_y, 0, pixel_height)
geotrans = (x0, dx, 0.0, y0, 0.0, dy)

# ============================================================
# Read CRS information (CF-style)
# ============================================================
proj = None
if "crs" in ds.variables:
    # WKT projection string written during NetCDF creation
    proj = ds.variables["crs"].spatial_ref

# ============================================================
# Prepare GDAL GeoTIFF driver
# ============================================================
driver = gdal.GetDriverByName("GTiff")

# ============================================================
# Loop over time dimension and export daily GeoTIFFs
# ============================================================
# Each time slice corresponds to one DOY
for i in range(ntime):
    # DOY stored directly in NetCDF (not assumed continuous)
    doy = int(time_var[i])

    # Output filename: YYYYDDD.tif
    out_tif = os.path.join(out_tif_dir, f"{year}{doy:03d}.tif")

    # Read ET data for the given day
    arr = et[i, :, :].astype(np.float32)

    # Create GeoTIFF
    dst = driver.Create(
        out_tif,
        nlon,
        nlat,
        1,
        gdal.GDT_Float32,
        options=[
            "COMPRESS=LZW",  # Lossless compression
            "TILED=YES"      # Tiling for better I/O performance
        ]
    )

    # Assign spatial reference
    dst.SetGeoTransform(geotrans)
    if proj:
        dst.SetProjection(proj)

    # Write raster band
    band = dst.GetRasterBand(1)
    band.WriteArray(arr)

    # Flush and close dataset
    band.FlushCache()
    dst = None

    print(f"Written: {out_tif}")

# ============================================================
# Close NetCDF dataset
# ============================================================
ds.close()

print("NC → GeoTIFF finished.")
