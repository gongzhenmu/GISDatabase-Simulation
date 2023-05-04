"""/content/drive/MyDrive/CS541Project/data/West_Lafayette.osm.pbf


/home/ubuntu/gistest/GISDatabase-Simulation/data/West_Lafayette.osm.pbf
table format [{id:,lon,lat}]

217754230

create shortestpath from 358665942 to 9519034907

create shortestpath from [-86.8801548,40.4246338 ] to [-86.8868154,40.4200306]

create shortestpath from 10087689850 to 9178785027  where service < 0.1


find restaurant from 358665942 where distance between 0 and 5

find restaurant from [-86.9359556,40.4365242] where distance between 2 and 4

find 5 restaurant from [-86.8945389,40.4183154]

find 7 library from 9178814647

find 2 bicycle_parking from 9844603592
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
