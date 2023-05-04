import networkx as nx
from rtree import index
from shapely.geometry import Point
import heapq
from haversine_distance import haversine_distance
import re


class GisDatabase:
    def __init__(self, queryProcessor, fileHandler):
        self.queryProcessor = queryProcessor
        self.handler = fileHandler
        self.rtree = None
        self.graph = nx.Graph()
        self.poi_index = None
        try:
          self.terminal()
        except Exception as e:
          print(str(e))

    def load_file(self, fileName):
        self.handler.apply_file(fileName)
        self.rtree = self.handler.rtree_edge
        self.deleteTables()
        self.createTables()
        self.fetchAll()
        self.graph.clear()
        self.create_graph()
        self.build_poi_index()

      
    def createPoiTable(self):
      self.queryProcessor.process_query("CREATE TABLE poi (id, name, amenity,shop)")
    def createNodeTable(self):
      self.queryProcessor.process_query("CREATE TABLE nodes (id, lon,lat)")
    def createEdgeTable(self):
      self.queryProcessor.process_query("CREATE TABLE edges (id, wid,start,end,distance,highway)")


    def createTables(self):
      self.createEdgeTable()
      self.createNodeTable()
      self.createPoiTable()
    def deleteTables(self):
      self.queryProcessor.process_query("drop table nodes")
      self.queryProcessor.process_query("drop table poi")
      self.queryProcessor.process_query("drop table edges")

    def fetchNode(self,id,lon,lat):
      query = "INSERT INTO nodes VALUES ({}, {}, {})".format(id,lon,lat)
      self.queryProcessor.process_query(query)
    def fetchEdge(self,id,wid,start,end,distance,highway):
      query = "INSERT INTO edges VALUES ({}, {}, {},{},{},{})".format(id,wid,start,end,distance,highway)
      self.queryProcessor.process_query(query)
    def fetchPOI(self,id,name,amenity,shop):
      query = "INSERT INTO poi VALUES ({}, {}, {},{})".format(id,name,amenity,shop)
      self.queryProcessor.process_query(query)
    
    def fetchNodes(self):
      for key, value in self.handler.nodes.items():
        self.fetchNode(key,value[0],value[1])

    def fetchEdges(self):
      for edge in self.handler.edges:
        self.fetchEdge(edge[0],edge[1],edge[2],edge[3],edge[4],edge[5])

    def fetchPOIs(self):
      for poi in self.handler.poi:
        self.fetchPOI(poi[0],poi[1],poi[2],poi[3])
    
    def fetchAll(self):
      print("Fetching nodes..............")
      self.fetchNodes()
      print("Fetching edges.............")
      self.fetchEdges()
      print("Fetching poi.............")
      self.fetchPOIs()
      print("Data Fetching Completed")

    def runQuery(self, query):
        query = query.strip().lower()
        if query.startswith("find"):
            if re.search(r"\d+ (.*?) from", query):
                self.process_find_k_nearest_pois_query(query)
            else:
                self.process_range_query(query)
        elif query.startswith("create shortestpath"):
            self.process_shortest_path_query(query)
        else:
            self.queryProcessor.process_query(query)

    def terminal(self):
        print("Enter your command (type 'quit' to exit, 'load file' to load a data file):")
        userInput = input(">>").lower()
        while userInput != 'quit':
            if userInput == 'load file':
                print("Enter the filename:")
                filename = input()
                self.load_file(filename)
                print("File loaded and tables recreated.")
            elif userInput == 'create graph':
                self.graph.clear()
                self.create_graph()
                print("A new graph has been created")
            else:
                self.runQuery(userInput)
            userInput = input(">>").lower()

    def create_graph(self):
        nodes = self.getTableData("nodes")
        for node in nodes:
            self.graph.add_node(int(node['id']), lon=float(node['lon']), lat=float(node['lat']))
        #print(self.graph.number_of_nodes())
        edges = self.getTableData("edges")
        for edge in edges:
            self.graph.add_edge(int(edge['start']), int(edge['end']), weight=float(edge['distance']), highway=edge['highway'])
        #print(self.graph.number_of_edges())

    def shortest_path(self, start_id, end_id):
        try:
            shortest_path = nx.dijkstra_path(self.graph, start_id, end_id, weight='weight')
            distance = nx.dijkstra_path_length(self.graph, start_id, end_id, weight='weight')
            # return path
            result = []
            for i in range(len(shortest_path) - 1):
                node1 = shortest_path[i]
                node2 = shortest_path[i + 1]

                edge_data = self.graph[node1][node2]
                edge = {
                    'start_node_id': node1,
                    'start_node_lon': self.graph.nodes[node1]['lon'],
                    'start_node_lat': self.graph.nodes[node1]['lat'],
                    'end_node_id': node2,
                    'end_node_lon': self.graph.nodes[node2]['lon'],
                    'end_node_lat': self.graph.nodes[node2]['lat'],
                    'distance': edge_data['weight'],
                    'highway_type': edge_data['highway']
                }
                result.append(edge)


            print(f"Total distance: {round(distance,2)} miles")
            self.queryProcessor.database.print_table("edges", selected_data=result)
        except nx.NetworkXNoPath:
            print("No path found between the given nodes.")
            return []


    def getTableData(self,tableName):
        query = "SELECT * FROM {}".format(tableName).strip().lower()
        return self.queryProcessor.select_data(query,False)



    def find_nearest_node(self, lon, lat):
        nearest_edge = list(self.rtree.nearest((lon,lat,lon,lat), 1))[0]
        query = "select * from edges where wid == {}".format(nearest_edge)
        temp = set()
        data = self.queryProcessor.select_data(query,False)
        for i in data:
          temp.add(i['start'])
          temp.add(i['end'])
        
        ids = list(temp)
        result = []

        for i in ids:
          coord = (self.graph.nodes[i]['lon'],self.graph.nodes[i]['lat'])
          distance = haversine_distance(lat,lon,coord[1],coord[0])
          result.append((i,distance))
        result = sorted(result, key=lambda x: x[1])
        return result[0][0]


    def get_by_id(self,id):
        query = "select * from nodes where id == {}".format(id).strip().lower()
        data = self.queryProcessor.select_data(query,False)
        return float(data[0]['lon']),float(data[0]['lat'])

    def get_by_coord(self,lon,lat):
        query = "select * from nodes where lon == {} and lat == {}".format(lon,lat).strip().lower()
        data = self.queryProcessor.select_data(query,False)
        return data[0]['id']

    def get_id_by_tag(self,table_name,tag):
        query = "select * from poi where amenity = '{}' or shop = '{}'".format(tag,tag).strip().lower()
        data = self.queryProcessor.select_data(query,False)
        return data['id']

    def process_shortest_path_query(self, query):
        match_id = re.match(r"create shortestpath from (\d+) to (\d+)", query)
        match_coord = re.match(r"create shortestpath from \[(.*),(.*)\] to \[(.*),(.*)\]", query)
        match_where_id = re.match(r"create shortestpath from (\d+) to (\d+) where (\w+) < ([\d.]+)", query)
        match_where_coord = re.match(r"create shortestpath from \[(.*),(.*)\] to \[(.*),(.*)\] where (\w+) < ([\d.]+)", query)
        #print(match_id)
        if match_where_id:
            start_id = int(match_where_id.group(1))
            lon,lat = self.get_by_id(start_id)
            start_id = self.find_nearest_node(lon, lat)


            end_id = int(match_where_id.group(2))
            lon,lat = self.get_by_id(end_id)
            end_id = self.find_nearest_node(lon, lat)

            label = match_where_id.group(3)
            distance = float(match_where_id.group(4))
            self.label_constraint_shortest_path(self.graph, start_id, end_id, label, distance)

            
        elif match_where_coord:
            start_lon = float(match_where_coord.group(1))
            start_lat = float(match_where_coord.group(2))
            end_lon = float(match_where_coord.group(3))
            end_lat = float(match_where_coord.group(4))

            start_id = self.find_nearest_node(start_lon, start_lat)
            end_id = self.find_nearest_node(end_lon, end_lat)

            label = match_where_coord.group(5)
            distance = float(match_where_coord.group(6))
            self.label_constraint_shortest_path(self.graph, start_id, end_id, label, distance)
        
        
        
        elif match_id:
            start_id = int(match_id.group(1))
            lon,lat = self.get_by_id(start_id)
            start_id = self.find_nearest_node(lon, lat)

            end_id = int(match_id.group(2))
            lon,lat = self.get_by_id(end_id)
            end_id = self.find_nearest_node(lon, lat)
            self.shortest_path(start_id, end_id)

        elif match_coord:
            start_lon = float(match_coord.group(1))
            start_lat = float(match_coord.group(2))
            end_lon = float(match_coord.group(3))
            end_lat = float(match_coord.group(4))

            start_id = self.find_nearest_node(start_lon, start_lat)
            end_id = self.find_nearest_node(end_lon, end_lat)
            self.shortest_path(start_id, end_id)


            
        else:
            print("Invalid shortestpath query")
            return

        # self.shortest_path(start_id, end_id)
        # self.queryProcessor.database.print_table("nodes", selected_data=self.queryProcessor.database.select_data("nodes", condition=lambda row: row["id"] in path))
        # return path


    def process_range_query(self, query):
      match_id = re.match(r"find ([\w\s]+) from (\d+) where distance between (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?)", query)
      match_coord = re.match(r"find ([\w\s]+) from \[(.*),(.*)\] where distance between (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?)", query)

      if match_id:
          tag = match_id.group(1)
          start_id = int(match_id.group(2))
          min_distance = float(match_id.group(3))
          max_distance = float(match_id.group(4))
          start_lon,start_lat =  self.get_by_id(start_id)
          self.build_poi_index()
          self.range_query(tag,start_lon,start_lat,max_distance, min_distance)
          

      elif match_coord:
          tag = match_id.group(1)
          start_lon= float(match_id.group(2))
          start_lat = float(match_id.group(3))
          min_distance = float(match_id.group(4))
          max_distance = float(match_id.group(5))
          self.build_poi_index()
          self.range_query(tag,start_lon,start_lat,max_distance, min_distance)
      else:
          print("Invalid range query")

    def range_query(self,tag,start_lon,start_lat, max_distance, min_distance):
       #print(tag,start_lon,start_lat, max_distance, min_distance)
       center = Point(start_lon,start_lat)
       radius = max_distance*1609.34
       circle = center.buffer(radius)
       result = list(self.poi_index.intersection((circle.bounds), objects=True))
       result = [(item.object, item.bbox[0],item.bbox[1]) for item in result if tag in item.object['amenity']  or tag in item.object['shop']]
       output = []
       for poi in result:
         distance = haversine_distance(start_lat,start_lon,poi[2],poi[1])
         if  distance <= max_distance and distance >= min_distance:
            output.append({ 'id': poi[0]['id'],
                            'name': poi[0]['name'], 
                             'amenity': poi[0]['amenity'],
                           'shop': poi[0]['shop'],
                           'lon': poi[1],
                           'lat': poi[2],
                           'distance':distance
                           })
       self.queryProcessor.database.print_table("poi", selected_data=output)



       
    def find_k_nearest_pois(self,tag,start_lon,start_lat,k):
      center = Point(start_lon,start_lat)
      result = list(self.poi_index.nearest(center.bounds, k, objects=True))
      result = [(item.object, item.bbox[0],item.bbox[1]) for item in result]
      output = []
      for poi in result:
        distance = haversine_distance(start_lat,start_lon,poi[2],poi[1])
        output.append({ 'id': poi[0]['id'],
                        'name': poi[0]['name'], 
                          'amenity': poi[0]['amenity'],
                        'shop': poi[0]['shop'],
                        'lon': poi[1],
                        'lat': poi[2],
                        'distance':distance
                        })
        
      self.queryProcessor.database.print_table("poi", selected_data=output)
      

    def insert_poi(self,poi):

        id = int(poi["id"])
        self.poi_index.insert(id, Point(float(self.graph.nodes[id]['lon']), float(self.graph.nodes[id]['lat'])).bounds, obj=poi)


    def build_poi_index(self):
      self.poi_index = index.Index()
      pois = self.getTableData("poi")
      for poi in pois:
        self.insert_poi(poi)

    def insert_poi_tag(self,poi,tag):
      if tag in poi['amenity'] or tag in poi['shop']:
        id = int(poi["id"])
        self.poi_index.insert(id, Point(float(self.graph.nodes[id]['lon']), float(self.graph.nodes[id]['lat'])).bounds, obj=poi)

    def build_k_nearest_poi_index(self,tag):
      self.poi_index = index.Index()
      pois = self.getTableData("poi")
      for poi in pois:
        self.insert_poi_tag(poi,tag)

    def process_find_k_nearest_pois_query(self, query):
      match_id = re.match(r"find (\d+) (.*?) from (\d+)", query)
      match_coord = re.match(r"find (\d+) (.*?) from \[(.*),(.*)\]", query)

      if match_id:
          k = int(match_id.group(1))
          label = match_id.group(2)
          start_id = int(match_id.group(3))
          start_lon, start_lat = self.get_by_id(start_id)
      elif match_coord:
          k = int(match_coord.group(1))
          label = match_coord.group(2)
          start_lon = float(match_coord.group(3))
          start_lat = float(match_coord.group(4))
      else:
          print("Invalid find k nearest pois query")
          return
      self.build_k_nearest_poi_index(label)
      self.find_k_nearest_pois( label, start_lon, start_lat,k)


    def total_distance_constrained_shortest_path(self,graph, source, target, limit_edge_type, limit_distance):
        visited = set()
        priority_queue = [(0, source, 0, [])]  # (distance, node, edge_type_distance, path)

        while priority_queue:
            dist, current, edge_type_dist, path = heapq.heappop(priority_queue)

            if current == target and edge_type_dist <= limit_distance:
                return path + [current]

            if current not in visited:
                visited.add(current)
                path = path + [current]

                for neighbor, data in graph[current].items():
                    if neighbor not in visited:
                        edge_distance = data['weight']
                        edge_type = data['highway']

                        new_edge_type_dist = edge_type_dist
                        if edge_type == limit_edge_type:
                            new_edge_type_dist += edge_distance

                        heapq.heappush(
                            priority_queue,
                            (dist + edge_distance, neighbor, new_edge_type_dist, path)
                        )

        return None  # No path found


    # def total_distance_constrained_shortest_path(self, graph, source, target, limit_edge_type, limit_distance):
    #     def dfs(current, visited, edge_type_dist, path):
    #         nonlocal best_path
    #         if current == target and edge_type_dist <= limit_distance:
    #             best_path = path + [current]
    #             return

    #         if current not in visited:
    #             visited.add(current)
    #             path = path + [current]

    #             for neighbor, data in graph[current].items():
    #                 if neighbor not in visited:
    #                     edge_distance = data['weight']
    #                     edge_type = data['highway']

    #                     new_edge_type_dist = edge_type_dist
    #                     if edge_type == limit_edge_type:
    #                         new_edge_type_dist += edge_distance

    #                     if best_path is None or len(path) + 1 < len(best_path):
    #                         dfs(neighbor, visited.copy(), new_edge_type_dist, path)

    #     best_path = None
    #     dfs(source, set(), 0, [])
    #     return best_path

    def label_constraint_shortest_path(self,graph, source, target, limit_edge_type, limit_distance):
      path = self.total_distance_constrained_shortest_path(graph, source, target, limit_edge_type, limit_distance)
      distance = 0
      result = []
      if path == None:
        print("No path found with {} less than {} miles".format(limit_edge_type,limit_distance))
        return
      for i in range(len(path) - 1):
          node1 = path[i]
          node2 = path[i + 1]

          edge_data = self.graph[node1][node2]
          edge = {
              'start_node_id': node1,
              'start_node_lon': self.graph.nodes[node1]['lon'],
              'start_node_lat': self.graph.nodes[node1]['lat'],
              'end_node_id': node2,
              'end_node_lon': self.graph.nodes[node2]['lon'],
              'end_node_lat': self.graph.nodes[node2]['lat'],
              'distance': edge_data['weight'],
              'highway_type': edge_data['highway']
          }
          result.append(edge)
          distance += float(edge_data['weight'])


      print(f"Total distance: {round(distance,2)} miles")
      self.queryProcessor.database.print_table("edges", selected_data=result)
      

    


     


      
