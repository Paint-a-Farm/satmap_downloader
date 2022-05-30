#!/usr/bin/python

from math import cos, sin
import math
import urllib.request
import os
import sys
import argparse
import time
import random
import concurrent.futures

from PIL import Image
from alive_progress import alive_bar

from convert import calc
from gmap_utils import latlon2xy

__version__ = "1.0.0"

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'
headers = {'User-Agent': USER_AGENT}


def individual_tile_download(x, y, zoom, pbar, satellite=True):
    """Download an individual tile

    Args:
        x (_type_): _description_
        y (_type_): _description_
        zoom (_type_): _description_
        pbar (_type_): _description_
        satellite (bool, optional): _description_. Defaults to True.
    """
    url = None
    filename = None

    if satellite:
        # url = "https://avoin-karttakuva.maanmittauslaitos.fi/avoin/wmts/1.0.0/ortokuva/default/WGS84_Pseudo-Mercator/%d/%d/%d.png?api-key=46eb0ff8-ec08-4c23-bc33-2f99f33260b8" % (zoom,y,x)
        url = "https://mt0.google.com/vt/lyrs=s&hl=en&x=%d&y=%d&z=%d&s=Ga" % (
            x, y, zoom)
        # print ("-- url", url)
        filename = "tiles/%d_%d_%d_s.png" % (zoom, x, y)
    else:
        url = "http://mt1.google.com/vt/lyrs=h@162000000&hl=en&x=%d&s=&y=%d&z=%d" % (
            x, y, zoom)
        filename = "tiles/%d_%d_%d_r.png" % (zoom, x, y)

    if not os.path.exists(filename):

        bytes = None

        try:
            req = urllib.request.Request(url, data=None, headers=headers)
            response = urllib.request.urlopen(req)
            bytes = response.read()
        except Exception as e:
            print("--", filename, "->", e)
            sys.exit(1)

        if bytes.startswith(b"<html>"):
            print("-- forbidden", filename)
            sys.exit(1)

        # print ("-- saving", filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'wb')
        f.write(bytes)
        f.close()

        time.sleep(random.random())
    pbar()


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite=True):

    start_x, start_y, _rXs, _rYs = latlon2xy(zoom, lat_start, lon_start)
    stop_x, stop_y, _rXe, _rYe = latlon2xy(zoom, lat_stop, lon_stop)

    # print ("x range", start_x, stop_x)
    # print ("y range", start_y, stop_y)
    total = (stop_y-start_y+1) * (stop_x-start_x+1)
    # print("total tiles", total)

    with alive_bar(total, title_length=20, title="Downloading tiles", theme='smooth') as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for x in range(start_x, stop_x+1):
                for y in range(start_y, stop_y+1):
                    executor.submit(individual_tile_download, x,
                                    y, zoom, pbar, satellite)

def merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, rotation, output, satellite=True):

    Image.MAX_IMAGE_PIXELS = 933120000
    TYPE, ext = 'r', 'png'
    if satellite:
        TYPE, ext = 's', 'png'

    x_start, y_start, remainX_start, remainY_start = latlon2xy(
        zoom, lat_start, lon_start)
    x_stop, y_stop, remainX_stop, remainY_stop = latlon2xy(
        zoom, lat_stop, lon_stop)

    # print ("x range", x_start, x_stop)
    # print ("y range", y_start, y_stop)

    # print (remainX_start, remainY_start, remainX_stop, remainY_stop)

    w = (x_stop + 1 - x_start) * 256
    h = (y_stop + 1 - y_start) * 256

    # print ("width:", w)
    # print ("height:", h)

    result = Image.new("RGB", (w, h))

    total = (y_stop-y_start+1) * (x_stop-x_start+1)
    with alive_bar(total, title_length=20, title="Merging tiles", theme='smooth') as pbar:
        for x in range(x_start, x_stop+1):
            for y in range(y_start, y_stop+1):
                # time.sleep(2)
                filename = "tiles/%d_%d_%d_%s.%s" % (zoom, x, y, TYPE, ext)

                if not os.path.exists(filename):
                    print("-- missing", filename)
                    continue

                x_paste = (x - x_start) * 256
                y_paste = h - (y_stop + 1 - y) * 256

                try:
                    i = Image.open(filename)
                except Exception as e:
                    print("-- %s, removing %s" % (e, filename))
                    trash_dst = os.path.expanduser("~/.Trash/%s" % filename)
                    os.rename(filename, trash_dst)
                    continue

                result.paste(i, (x_paste, y_paste))

                del i
                pbar(1.)

    with alive_bar(title_length=20, title="Preparing image", monitor=False, stats=False, manual=True, bar=False) as pbar:

        # print((remainX_start, remainY_start, w-(256-remainX_stop), h-(256-remainY_stop)))
        cropped = result.crop(
            (remainX_start, remainY_start, w-(256-remainX_stop), h-(256-remainY_stop)))
        rotated = cropped.rotate(rotation, expand=False)
        newWidth = (1*cos(math.radians(abs(rotation))) +
                    1*sin(math.radians(abs(rotation))))
        # print ('--newWidth', newWidth)

        ratio = 1/newWidth
        # print(('-- ratio', ratio))
        # print(('-- cropped.width', cropped.width))
        # print(('-- cropped.height', cropped.height))
        # print(('-- rotated.width', rotated.width))
        # print(('-- rotated.height', rotated.height))

        box = (int((rotated.width - ratio*rotated.width)/2), int((rotated.height - ratio*rotated.height)/2), int(rotated.width -
               (rotated.width - ratio*rotated.width)/2), int(rotated.height - (rotated.height - ratio*rotated.height)/2))

        # print(box)

        cropped2 = rotated.crop(box)
        cropped2 = cropped2.resize((int(min(cropped2.width, cropped2.height)), int(
            min(cropped2.width, cropped2.height))))

        cropped2.save(output)
        pbar(1.)
        pbar.text('Done!')
    print('Saved image as \033[1m' + output + '\033[0m')


def list_str(values):
    return values.split(',')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='satmap_downloader.exe',
        description='Google Maps Satellite Image Downloader')
    parser.add_argument(
        '--version', help='Program version', action='version', version=__version__)
    parser.add_argument(
        '--origin', help='Coordinates of the top left corner of the area to download as latitude,longitude', type=list_str, required=True)
    parser.add_argument(
        '--size', help='Area height/width in meters (assumes square terrain)', type=float, required=True)
    parser.add_argument(
        '--rotation', help='Rotation of the terrain area in degrees', type=float, default=0)
    parser.add_argument(
        '--zoom', help='Desired zoom level of the satellite image', type=int, default=17)
    parser.add_argument('--output', help='Output file name',
                        type=str, default='mymap.png', required=True)
    args = parser.parse_args()

    zoom = args.zoom
    lat_start, lon_start = float(args.origin[0]), float(args.origin[1])
    size = args.size
    filename = args.output
    rotation = args.rotation

    with alive_bar(title_length=20, title="Calculating boundary", monitor=False, stats=False, manual=True, bar=False) as pbar:
        lons, lats = calc(lon_start, lat_start, rotation, size)
        pbar(1.)

    download_tiles(zoom, max(lats), min(lats),
                   min(lons), max(lons), satellite=True)
    merge_tiles(zoom, max(lats), min(lats), min(lons),
                max(lons), rotation, filename, satellite=True)
