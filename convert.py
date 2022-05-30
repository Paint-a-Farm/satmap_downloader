import pyproj
# import folium
from math import radians, sqrt, cos, sin

def calc(lon, lat, rotation, size):

  newWidth = size*cos(radians(abs(rotation))) + size*sin(radians(abs(rotation)))
  ratio=size/newWidth

  toprightlon, toprightlat, _ = pyproj.Geod(ellps='WGS84').fwd(lon, lat, 90+rotation, size)
  bottomrightlon, bottomrightlat, _ = pyproj.Geod(ellps='WGS84').fwd(toprightlon, toprightlat, 180+rotation, size)
  bottomleftlon, bottomleftlat, _ = pyproj.Geod(ellps='WGS84').fwd(bottomrightlon, bottomrightlat, 270+rotation, size)

  lons = [lon, toprightlon, bottomrightlon, bottomleftlon]
  lats = [lat, toprightlat, bottomrightlat, bottomleftlat]

  return lons, lats

if __name__ == "__main__":

  lon = 24.780973
  lat = 64.806165
  rotation = 10
  size = 2048
  
  lons, lats = calc(lon, lat, rotation, size)

  # print (f'coordinates: {lon:.6f} {lat:.6f} {bottomrightlon:.6f} {bottomrightlat:.6f}')
  print ((f'boundingbox: {min(lons):.6f} {max(lats):.6f} {max(lons):.6f} {min(lats):.6f}'))
  # print (f'width: {newWidth:.6f}')
  # print (f'ratio: {ratio:.6f}')

  # m = folium.Map(location=[40.0150, -105.2705])
  # m


  #  25.713441 65.145231 25.757060 65.126856