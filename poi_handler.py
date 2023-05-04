import osmium
import math
from shapely.geometry import Point, LineString
from rtree import index
from haversine_distance import haversine_distance

class POIHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.tags = ['name','amenity','shop']
        self.wayTags = ['highway']
        self.nodes = {}
        self.edges = []
        self.poi = set()
        self.index = 0
        self.rtree_edge = index.Index()

    def node(self, n):
        self.nodes[n.id] = (n.location.lon, n.location.lat)
        node_tags = {tag.k: tag.v for tag in n.tags if tag.k in self.tags}
        # ID,highway,amenity,name,shop
        if len(node_tags) !=0:
          node_data = [n.id]
          for tag in self.tags:
            if tag in node_tags:
              node_data.append(node_tags[tag])
            else:
              node_data.append('')
            
          self.poi.add(tuple(node_data))

    def way(self, w):
        highway = ""
        line_list = []
        for tag in w.tags:
          if tag.k in self.wayTags:
            highway = tag.v
        for i in range(len(w.nodes) - 1):
            node1 = w.nodes[i].ref
            node2 = w.nodes[i + 1].ref

            if node1 in self.nodes and node2 in self.nodes:
                line_list.append(list(self.nodes[node1]))
                line_list.append(list(self.nodes[node2]))
                lon1, lat1 = self.nodes[node1]
                lon2, lat2 = self.nodes[node2]
                distance = haversine_distance(lat1, lon1, lat2, lon2)

                self.edges.append((self.index,w.id,node1, node2, distance,highway))
                self.index +=1
        if len(line_list) >0:
            self.rtree_edge.insert(w.id, LineString(line_list).bounds)

