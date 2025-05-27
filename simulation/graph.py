import json
#from creature import Creature

class Tile:
    """
    This is a mathematical representation of a single tile of the simulation. This class would be capable of quickly returning
    Nodes neightbours, intacting the inner connections of the graph from json as well as to handle both hexagons and pentagons
    """
    def __init__(self, tile_id, v = []):
        self.tile_id = tile_id
        self.v = set(v) #supposed to be vertices, we do not use them for any other reason besides inital creation
        self.neightbours = set()
        self.state = None #empty
        self.energy = 5 #/100
        self.decay_factor = 1 - 0.075
        self.end_cap = 121

    def add_neightbour(self, nid):
        self.neightbours.add(nid)

    def add_energy(self, val):
        #energy decays and capped at 1000
        self.energy = self.energy + val
        if (self.energy > self.end_cap):
            self.energy = self.end_cap
        self.energy *= self.decay_factor
 
class Graph:
    """
    Here is a classical graph data structure.
    """
    def __init__(self):
        self.tiles = {}
    
    def add_tile(self, tile_id):
        self.tiles[tile_id] = Tile(tile_id)
    
    def set_state(self, location, creature):
        self.tiles[location].state = creature

    def link_neightbours(self, tile_id1, tile_id2):
        self.tiles[tile_id1].add_neightbour(tile_id2)
        self.tiles[tile_id2].add_neightbour(tile_id1)

    def get_n(self, tile_id):
        a = list(self.tiles[tile_id].neightbours)
        res = []
        for el in a:
            res.append(self.tiles[el])
        return res
    
    def get_tile(self,tile_id):
        return self.tiles.get(tile_id)

    def build_graph(self, faces):
        #A map of faces which out graphical renderer is using is used here as well to contruct a graph,
        #which we would later be able to populate with creatures. For all faces that share 2 same points (we make sets enumarate and compare)
        #We consider triangles as neightbours, and an [a,b,c] element as a face

        dct = {}
        for idx, f in enumerate(faces):
            tile = Tile(idx,f)
            self.tiles[idx] = tile
            
            for edge in self.getSides(f):
                k = tuple(sorted(edge))
                dct.setdefault(k, []).append(idx)
            
        for t in self.tiles.values():
            f = t.v
            cand = set()
            for e in self.getSides(f):
                key = tuple(sorted(e))
            
                for nid in dct.get(key, []):
                    if nid != t.tile_id:
                        cand.add(nid)

            for nid in cand:
                other_face = self.tiles[nid].v
                if len(f.intersection(other_face)) == 2:
                    t.add_neightbour(nid)

    def getSides(self, f):
        v = list(f)
        return [(v[0], v[1]), (v[1], v[2]), (v[2], v[0])]
    
    def debug_tiles(self):
        for t in self.tiles.values():
            print(t.tile_id, t.neightbours, t.state)
            break
    
    def update(self, lst):
        #given new eergy desposition fill tiles with energy, if to much energy cap at 100 (ENERGY DECAYS)
        counter = 0
        for t in self.tiles:
            self.tiles[counter].add_energy(lst[counter])
            counter+=1

if __name__ == "__main__":
    """
    Space for test runs from this file. During real use I would be refering to graph.py from different files.
    """
    with open("faces.json", "r") as f:
        faces = json.load(f)


    graph = Graph()
    graph.build_graph(faces)
    graph.debug_tiles()