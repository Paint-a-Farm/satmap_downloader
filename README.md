# Satellite Image Downloader for Farming Simulator

## Installation

Download the latest executable for your platform from the Releases page to your computer. The script will download all tiles to a `tiles` folder that it creates in the same directory as the executable.

## Usage
```
usage: satmap_downloader [-h] [--version] --origin ORIGIN --size SIZE [--rotation ROTATION] [--zoom ZOOM] --output OUTPUT

Google Maps Satellite Image Downloader

optional arguments:
  -h, --help           show this help message and exit
  --version            Program version
  --origin ORIGIN      Coordinates of the top left corner of the area to download as latitude,longitude
  --size SIZE          Area height/width in meters (assumes square terrain)
  --rotation ROTATION  Rotation of the terrain area in degrees
  --zoom ZOOM          Desired zoom level of the satellite image
  --output OUTPUT      Output file name
```

The script will download all tiles to a `tiles` folder that it creates in the same directory as the executable, and save the final image in the location specified with the output parameter.

## Parameters

| Parameter | Description |
| --------- | ----------- |
| `origin` | Coordinates of the top left corner of the area to download as latitude,longitude.<br>Example: `--origin=48.787077, 25.727360`                                          |
| `size` | Area height/width in meters (assumes square terrain).<br>Example: `--size=2048`|
| `rotation` | Rotation of the terrain area in degrees. |
| `zoom` | Desired zoom level of the satellite image.<br>This setting determines the resolution of the satellite image.<br>For more information on zoom levels see: https://wiki.openstreetmap.org/wiki/Zoom_levels<br>Example: `--zoom=18` |
| `output` | Output file name.<br>Example: `--output=mysatelliteimage.png` |

## I don't trust your executables

Fair enough, you can also download the sources from this repo and run the `download_tiles.py` script instead with the same parameters as above.

Make sure you have the `Pillow`, `alive_progress` and `pyproj` packages installed first:

```bash
> python -m pip install Pillow alive_progress pyproj

> python ./download_tiles.py --origin ...
```