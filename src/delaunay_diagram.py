import numpy as np
import scipy.spatial
import spherical_geometry.polygon as geom

import sys

import src.point as point

from statistics import median


class Triangle:
    def __init__(self, area, corners):
        if 2 * np.pi < area < 4 * np.pi:
            area = 4 * np.pi - area
        self.area = area
        self.adjacent = set()
        self.points = corners


class DelaunayDiagram:
    """
    Variables:
     - neighbours: dictionary that for each point holds a set of points that are its neighbours
     - neighbours_making_triangles: for each neighbouring points returns a set of points that make are common neighbour
       with the two making the key
     - triangles: a dictionary that for tuples of points contains triangle areas
    """

    def __init__(self, points):
        cartesian_points = [p.get_cartesian_coordinates([0, 0, 0], 1) for p in points]
        delaunay = scipy.spatial.ConvexHull(cartesian_points)

        self.neighbours = {p: set() for p in points}
        self.neighbours_making_triangles = {}
        self.triangles = {}
        self.triangles_by_points = {p: set() for p in points}

        for simplice in delaunay.simplices:
            pts = [points[v] for v in simplice]
            self.neighbours[pts[0]].add(pts[1])
            self.neighbours[pts[0]].add(pts[2])
            self.neighbours[pts[1]].add(pts[0])
            self.neighbours[pts[1]].add(pts[2])
            self.neighbours[pts[2]].add(pts[0])
            self.neighbours[pts[2]].add(pts[1])

            neighbouring_triangles = set()

            if (pts[0], pts[1]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[0], pts[1])] = set()
            else:
                neighbouring_triangles.update([
                    self.triangles[(pts[0], pts[1], p)] for p in self.neighbours_making_triangles[(pts[0], pts[1])]]
                )
            self.neighbours_making_triangles[(pts[0], pts[1])].add(pts[2])
            if (pts[1], pts[0]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[1], pts[0])] = set()
            self.neighbours_making_triangles[(pts[1], pts[0])].add(pts[2])
            if (pts[0], pts[2]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[0], pts[2])] = set()
            else:
                neighbouring_triangles.update([
                    self.triangles[(pts[0], pts[2], p)] for p in self.neighbours_making_triangles[(pts[0], pts[2])]]
                )
            self.neighbours_making_triangles[(pts[0], pts[2])].add(pts[1])
            if (pts[2], pts[0]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[2], pts[0])] = set()
            self.neighbours_making_triangles[(pts[2], pts[0])].add(pts[1])
            if (pts[1], pts[2]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[1], pts[2])] = set()
            else:
                neighbouring_triangles.update([
                    self.triangles[(pts[1], pts[2], p)] for p in self.neighbours_making_triangles[(pts[1], pts[2])]]
                )
            self.neighbours_making_triangles[(pts[1], pts[2])].add(pts[0])
            if (pts[2], pts[1]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[2], pts[1])] = set()
            self.neighbours_making_triangles[(pts[2], pts[1])].add(pts[0])

            triangle = Triangle(geom.SphericalPolygon(
                [p.get_cartesian_coordinates([0, 0, 0], 1) for p in pts],
                [0, 0, 0]).area(), set(pts))

            for t in neighbouring_triangles:
                t.adjacent.add(triangle)
                triangle.adjacent.add(t)

            self.triangles[(pts[0], pts[1], pts[2])] = triangle
            self.triangles[(pts[0], pts[2], pts[1])] = triangle
            self.triangles[(pts[1], pts[0], pts[2])] = triangle
            self.triangles[(pts[1], pts[2], pts[0])] = triangle
            self.triangles[(pts[2], pts[0], pts[1])] = triangle
            self.triangles[(pts[2], pts[1], pts[0])] = triangle

            self.triangles_by_points[pts[0]].add(triangle)
            self.triangles_by_points[pts[1]].add(triangle)
            self.triangles_by_points[pts[2]].add(triangle)


if __name__ == "__main__":
    # print delaunay diagram's statistics for the first argument
    input_file = sys.argv[1]
    points = point.load_from_csv(input_file)

    delaunay = DelaunayDiagram(points)
    triangles = len(delaunay.triangles) / 6
    total_area = sum(t.area for t in delaunay.triangles.values()) / 6
    average_area = total_area / triangles
    median_area = median(t.area for t in delaunay.triangles.values())
    max_area = max(t.area for t in delaunay.triangles.values())
    min_area = min(t.area for t in delaunay.triangles.values())

    print("""
    Total triangles: {}
    Total area: {} (Theoretical: 4 * pi = 12.566)
    Max area: {}
    Min area: {}
    Average area: {}
    Median area: {}
    Density: {}
    """.format(triangles, total_area, max_area, min_area, average_area, median_area, len(points)/total_area))
