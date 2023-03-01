import osmium
import sys

class NamesHandler(osmium.SimpleHandler):
    def __init__(self):
        super(NamesHandler, self).__init__()
        self.nodes = {}
        self.ways = {}
        self.relations = {}

    
    def node(self, n):
      location = str(n.location).split("/")
      self.nodes[n.id] = {'lat':float(location[0]),'lon':float(location[1]),'tags':str(n.tags)}
    def way(self,w):
      mylist = [int(str(i).split("@")[0]) for i in w.nodes]
      self.ways[w.id] = {'nodes':mylist,'tags':str(w.tags)}
    def relation(self,r):
      mylist = []
      for i in r.members:
        id = str(i).split("@")[0]
        myTuple = (id[0],int(id[1:]))
        mylist.append(myTuple)

      self.relations[r.id] = {'members':mylist, 'tags':str(r.tags)}



x =  NamesHandler()
x.apply_file('/content/drive/MyDrive/CS541Project/map.xml', locations=True)

for key,item in x.nodes.items():
  print(key,item)

for key,item in x.ways.items():
  print(key,item)

for key,item in x.relations.items():
  print(key,item)
