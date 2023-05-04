"""/content/drive/MyDrive/CS541Project/data/West_Lafayette.osm.pbf


/home/ubuntu/GISDatabase/data/West_Lafayette.osm.pbf
table format [{id:,lon,lat}]

217754230

create shortestpath from 358665942 to 9519034907


find restaurant from 358665942 where distance between 0 and 5

find 5 restaurant from [-86.8945389,40.4183154]
"""
from database import Database
from query_processor import QueryProcessor
from poi_handler import POIHandler
from gis_database import GisDatabase

db = Database()
qp = QueryProcessor(db)
geoHandler = POIHandler()
db = GisDatabase(qp,geoHandler)
db.terminal()
