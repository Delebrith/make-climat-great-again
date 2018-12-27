import scipy.spatial
import spherical_geometry.polygon as geom


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

        for simplice in delaunay.simplices:
            pts = [points[v] for v in simplice]
            self.neighbours[pts[0]].add(pts[1])
            self.neighbours[pts[0]].add(pts[2])
            self.neighbours[pts[1]].add(pts[0])
            self.neighbours[pts[1]].add(pts[2])
            self.neighbours[pts[2]].add(pts[0])
            self.neighbours[pts[2]].add(pts[1])

            if (pts[0], pts[1]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[0], pts[1])] = set()
            self.neighbours_making_triangles[(pts[0], pts[1])].add(pts[2])
            if (pts[1], pts[0]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[1], pts[0])] = set()
            self.neighbours_making_triangles[(pts[1], pts[0])].add(pts[2])
            if (pts[0], pts[2]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[0], pts[2])] = set()
            self.neighbours_making_triangles[(pts[0], pts[2])].add(pts[1])
            if (pts[2], pts[0]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[2], pts[0])] = set()
            self.neighbours_making_triangles[(pts[2], pts[0])].add(pts[1])
            if (pts[1], pts[2]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[1], pts[2])] = set()
            self.neighbours_making_triangles[(pts[1], pts[2])].add(pts[0])
            if (pts[2], pts[1]) not in self.neighbours_making_triangles:
                self.neighbours_making_triangles[(pts[2], pts[1])] = set()
            self.neighbours_making_triangles[(pts[2], pts[1])].add(pts[0])

            triangle_area = geom.SphericalPolygon(
                [p.get_cartesian_coordinates([0, 0, 0], 1) for p in pts],
                [0, 0, 0]).area()

            self.triangles[(pts[0], pts[1], pts[2])] = triangle_area
            self.triangles[(pts[0], pts[2], pts[1])] = triangle_area
            self.triangles[(pts[1], pts[0], pts[2])] = triangle_area
            self.triangles[(pts[1], pts[2], pts[0])] = triangle_area
            self.triangles[(pts[2], pts[0], pts[1])] = triangle_area
            self.triangles[(pts[2], pts[1], pts[0])] = triangle_area
