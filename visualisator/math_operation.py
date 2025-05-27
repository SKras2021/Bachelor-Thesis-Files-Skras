import json
from typing import List
from collections import defaultdict
from itertools import combinations
import itertools
import math
import time

def load():
    with open('backup/faces.json', 'r') as file:
        faces = json.load(file)
        
    with open('backup/vertices2D.json', 'r') as file:
        vertices = json.load(file)

    faces = list(faces)
    vertices = list(vertices)

    return faces, vertices

def save_v(new_vertices):
    with open("vertices2D.json", "w") as f:
        json.dump(new_vertices, f, separators=(',', ':'))
    return new_vertices

def save_f(vertices, new_faces):
    with open("faces.json", "w") as f:
        json.dump(new_faces, f, separators=(',', ':'))
    return vertices, new_faces

def get_faces_dualed(vertices):
    def distance(v1,v2):
        return math.sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2+(v1[2]-v2[2])**2)

    tolerance = 10
    new_faces = []

    first_min = float('inf')
    second_min = float('inf')

    for v in vertices:
        dist = distance(v,vertices[0])
        if (dist != 0 and dist < first_min):
            first_min = dist

    for i in range(len(vertices)):
        face = [i]
        for j in range(len(vertices)):
            a = distance(vertices[i],vertices[j])
            if ((a != 0 and (abs(a-first_min) < tolerance))):
                face.append(j)
        
        for j in range(0,len(face)):
            for k in range(j+1, len(face)):
                a = distance(vertices[face[j]],vertices[face[k]])
                if ((a != 0 and (abs(a-first_min) < tolerance))):
                    if (i != face[j] and face[j] != face[k] and face[k] != i):
                        candidate = sorted([i,face[j],face[k]])
                        if (candidate not in new_faces):
                            new_faces.append(candidate)

    return vertices, new_faces

def get_faces_trucated(vertices):
    def distance(v1, v2):
        return math.sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

    tolerance = 5
    new_faces = []

    # Find the smallest nonzero distance between any two vertices
    first_min = float('inf')
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            dist = distance(vertices[i], vertices[j])
            if 0 < dist < first_min:
                first_min = dist

    edges = defaultdict(set)

    # Create adjacency list where each vertex is connected to its 3 closest neighbors
    for i in range(len(vertices)):
        neighbors = []
        for j in range(len(vertices)):
            if i != j:
                dist = distance(vertices[i], vertices[j])
                if abs(dist - first_min) < tolerance:
                    neighbors.append(j)
            if len(neighbors) == 3:
                break
        edges[i].update(neighbors)

    # Function to find pentagonal and hexagonal faces
    def find_faces(graph, num_sides):
        faces = []
        for start in graph:
            paths = [[start]]

            # Build paths of the required length
            for _ in range(num_sides - 1):
                new_paths = []
                for path in paths:
                    last = path[-1]
                    for neighbor in graph[last]:
                        if neighbor not in path:
                            new_paths.append(path + [neighbor])
                paths = new_paths
            
            # Check if the paths form valid cycles
            for path in paths:
                if path[-1] in graph[path[0]]:  # Cycle check
                    face = sorted(path)
                    bl = True;
                    for el in faces:
                        if (sorted(el) == face):
                            bl = False;
                    if bl:
                        faces.append(path)
        return faces

    # Find pentagons and hexagons
    pentagons = find_faces(edges, 5)
    hexagons = find_faces(edges, 6)

    new_faces.extend(pentagons)
    new_faces.extend(hexagons)
    #print(len(new_faces))
    return vertices, new_faces

def truncate(faces,vertices):
    edges = set()

    for face in faces:
        sorted_face = sorted(face) 
        num_vertices = len(sorted_face)
        
        for i in range(num_vertices):
            a, b = sorted([sorted_face[i], sorted_face[(i + 1) % num_vertices]]) 
            edges.add((a, b))


    lines = [list(edge) for edge in sorted(edges)]

    new_vertices = []

    counter = 0
    for line in lines:
        p1, p2 = vertices[line[0]], vertices[line[1]]
        v1 = [(1 - 0.3333) * p1[i] + 0.3333 * p2[i] for i in range(3)]
        v2 = [(1 - 0.6666) * p1[i] + 0.6666 * p2[i] for i in range(3)]
        
        new_vertices.append(v2)
        new_vertices.append(v1)

    new_vertices = [list(x) for x in set(tuple(sub) for sub in new_vertices)] 
    return new_vertices

def dual(faces,vertices):
    new_vertices = []
    for face in faces:
        k = [
            sum(vertices[i][j] for i in face) / len(face)
            for j in range(len(vertices[0]))
        ]
        if k not in new_vertices:
            new_vertices.append(k)
    return new_vertices

faces, vertices = load()


vertices = save_v(vertices)
vertices, faces = save_f(*get_faces_dualed(vertices))

vertices = save_v(truncate(faces, vertices))
vertices, faces = save_f(*get_faces_trucated(vertices))

for i in range(2):
    vertices = save_v(dual(faces, vertices))
    vertices, faces = save_f(*get_faces_dualed(vertices))
    vertices = save_v(truncate(faces, vertices))
    vertices, faces = save_f(*get_faces_trucated(vertices))

#here we finalize MUST be truncated

new_vertices = []
for face in faces:
    k = [
        sum(vertices[i][j] for i in face) / len(face)
        for j in range(len(vertices[0]))
    ]
    if k not in new_vertices:
        new_vertices.append(k)

shift_val = len(new_vertices)
new_vertices = new_vertices + vertices

new_faces = []

for i in range(len(faces)):
    for j in range(-1,len(faces[i])-1):
        new_faces.append([i, faces[i][j]+shift_val, faces[i][j+1]+shift_val])

save_v(new_vertices)
save_f(new_vertices,new_faces)