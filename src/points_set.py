class PointsSet:
    def __init__(self, delaunay_diagram, initial_point, minimal_point_density, minimal_regression):
        self._delaunay = delaunay_diagram
        self._points = {initial_point}

        self._triangles = set()

        self._points_to_add = set()
        potential_points_to_add = set(delaunay_diagram.neighbours[initial_point])
        for p in potential_points_to_add:
            if p.regression > minimal_regression:
                self._points_to_add.add(p)

        self._points_to_remove = set()

        self._minimal_regression = minimal_regression
        self._minimal_point_density = minimal_point_density
        self._area = 0

    def _can_remove(self, point):
        if len(self._points) == 1:
            return False
        if len(self._points) <= 3:
            return True

        # check if there are no points left that are not a part of triangle
        for p in self._delaunay.neighbours[point].intersection(self._points):
            can_be_left = False
            for t in self._delaunay.triangles_by_points[p].intersection(self._triangles):
                if point not in t.points:
                    can_be_left = True
                    break

            if not can_be_left:
                return False

        # check left triangles consistency
        triangles_to_reach = {t for t in self._triangles if point not in t.points}

        reached = [triangles_to_reach.pop()]

        while len(reached) > 0:
            triangle = reached.pop()

            new_reached = triangle.adjacent.intersection(triangles_to_reach)
            reached.extend(new_reached)
            triangles_to_reach -= new_reached

        return len(triangles_to_reach) == 0

    def add_point(self, point):
        """

        :param point: Point to add, must be in points_to_add
        :return: None
        """

        self._points.add(point)

        if len(self._points) == 2:
            self._points_to_add = set()
        else:
            self._points_to_add.remove(point)

        for p in self._delaunay.neighbours[point].intersection(self._points):
            for m in self._delaunay.neighbours_making_triangles[(point, p)]:
                if m not in self._points and m.regression > self._minimal_regression:
                        self._points_to_add.add(m)
                else:
                    triangle = self._delaunay.triangles[(point, p, m)]
                    self._triangles.add(triangle)
                    self._area += triangle.area

        self._points_to_remove = {p for p in self._points if self._can_remove(p)}

    def remove_point(self, point):
        """

        :param point: Point to remove, must be in points_to_remove
        :return: None
        """

        self._points.remove(point)

        removed_triangles = self._delaunay.triangles_by_points[point].intersection(self._triangles)
        self._triangles -= removed_triangles
        self._area -= sum(t.area for t in removed_triangles)

        if len(self._points) == 1:
            potential_points_to_add = set(self._delaunay.neighbours[self._points.__iter__().__next__()])
            for p in potential_points_to_add:
                if p.regression > self._minimal_regression:
                    self._points_to_add.add(p)

        else:
            for p in self._delaunay.neighbours[point].intersection(self._points_to_add):
                for n in self._delaunay.neighbours[p].intersection(self._points):
                    if len(self._delaunay.neighbours_making_triangles[(p, n)].intersection(self._points)) > 0:
                        self._points_to_add.remove(p)
                        break

            self._points_to_add.add(point)

        self._points_to_remove = {p for p in self._points if self._can_remove(p)}

    def _get_value(self, points_n, area):
        if area == 0:
            return 0
        density = (points_n / area)

        return area if density >= self._minimal_point_density else (self._minimal_point_density / density)**2 * area

    def value_with_added(self, point):
        area = self._area + sum(
            t.area for t in self._delaunay.triangles_by_points[point] if t.points.issubset(self._points))

        return self._get_value(len(self._points) - 1, area)

    def value_with_removed(self, point):
        area = self._area - sum(
            t.area for t in self._delaunay.triangles_by_points[point].intersection(self._triangles))

        return self._get_value(len(self._points) - 1, area)

    @property
    def points_to_add(self):
        return self._points_to_add

    @property
    def points_to_remove(self):
        return self._points_to_remove

    @property
    def value(self):
        return self._get_value(len(self._points), self._area)

    @property
    def points(self):
        return self._points

    @property
    def has_minimal_density(self):
        return len(self._points) >= self._minimal_point_density * self._area
