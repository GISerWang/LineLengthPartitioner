# -*- coding: utf-8 -*-
import geopandas as gpd
import psycopg2
from geopandas import GeoSeries
from utils.LineLengthPartitionerUtils import Process
from utils.LineLengthPartitionerUtils import MultiLineString2LineString
params = {
    "meters": 400,
    "idField": "FFID",
    "geometryField": "geometry",
    "outFilePath": r'F:\res\out1202.shp'
}
# conn = psycopg2.connect(database="road", user="postgres", password="123456", host="localhost")
# sql = 'select %s,%s from gdsanhuan'%(params['idField'],params['geometryField'])
# origDf = gpd.GeoDataFrame.from_postgis(sql, con=conn, geom_col=params['geometryField'])
origDf = gpd.GeoDataFrame.from_file(r"F:\res\wgsroad.shp",geom_col=params['geometryField'])
origDf.to_crs('epsg:3857',inplace=True)
lineInfoArr = MultiLineString2LineString(origDf,params)
Process(lineInfoArr, params)
gs = []
ids = []
for lineInfo in lineInfoArr:
    for segment in lineInfo.getSegment():
        ids.append(lineInfo.id)
        gs.append(segment)
result = gpd.GeoDataFrame(geometry=GeoSeries(gs))
result["id"] = ids
result.crs = "EPSG:3857"
result.to_crs('epsg:4326',inplace=True)
result.to_file(driver='ESRI Shapefile',filename=params["outFilePath"])


