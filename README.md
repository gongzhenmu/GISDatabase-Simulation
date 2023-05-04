

### Features

Basic sql operations:<br> create table, insert value, delete value, drop table, select<br>
GIS related operations: <br>
create shortestpath based on id or coordinates<br>
range query from given location (id or coordinates)<br>
find K nearest poi from given location<br>

Query support:<br>
create shortestpath from {id} to {id}<br>
create shortestpath from [lon,lat] to [lon,lat]<br>
create shortestpath from {id} to {id} where label < {number in miles}<br>
create shortestpath from [lon,lat] to [lon,lat] where label < {number in miles}<br>
find {label} from {id} where distance between 0 and 5 (range in miles)<br>
find {label} from [lon,lat]] where distance between 0 and 5 (range in miles)<br>
find 5 {label} from [-86.8945389,40.4183154]<br>

### Python library
!pip install rtree networkx  osmium shapely 

### Start the database

1.python3 main.py
2.Enter "load file"
3.Run queries

### Query examples:
Basic: 
select * from poi
select * from nodes where id > 9519034907


GIS:

create shortestpath from 358665942 to 9519034907

create shortestpath from [-86.8801548,40.4246338 ] to [-86.8868154,40.4200306]

create shortestpath from 10087689850 to 9178785027  where service < 0.1


find restaurant from 358665942 where distance between 0 and 5

find restaurant from [-86.9359556,40.4365242] where distance between 2 and 4

find 5 restaurant from [-86.8945389,40.4183154]

find 7 library from 9178814647

find 2 bicycle_parking from 9844603592

