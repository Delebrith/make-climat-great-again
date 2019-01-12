class PointsSet:
    def __init__(self, delaunay_diagram, initial_point, minimal_point_density, minimal_regression):
        self._delaunay = delaunay_diagram
        self._points = {initial_point}

        self._triangles = set()

        self._points_to_add = set(p for p in delaunay_diagram.neighbours[initial_point]
                                  if p.regression > minimal_regression)

        self._points_to_remove = set()

        self._minimal_regression = minimal_regression
        self._minimal_point_density = minimal_point_density
        self._area = 0
        self._value = 0

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

        reached = [triangles_to_reach.pop()] if len(triangles_to_reach) > 0 else []

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

        new_triangles = set()
        for p in self._delaunay.neighbours[point].intersection(self._points):
            for m in self._delaunay.neighbours_making_triangles[(point, p)]:
                if m not in self._points:
                    if m.regression > self._minimal_regression:
                        self._points_to_add.add(m)
                else:
                    triangle = self._delaunay.triangles[(point, p, m)]
                    new_triangles.add(triangle)

        self._area += sum(t.area for t in new_triangles)
        self._triangles.update(new_triangles)

        self._points_to_remove = {p for p in self._points if self._can_remove(p)}
        self._value = self._get_value(len(self._points), self._triangles)

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
            self._points_to_add = set(p for p in self._delaunay.neighbours[self._points.__iter__().__next__()]
                                      if p.regression > self._minimal_regression)

        else:
            for p in self._delaunay.neighbours[point].intersection(self._points_to_add):
                for n in self._delaunay.neighbours[p].intersection(self._points):
                    if len(self._delaunay.neighbours_making_triangles[(p, n)].intersection(self._points)) > 0:
                        self._points_to_add.remove(p)
                        break

            self._points_to_add.add(point)

        self._points_to_remove = {p for p in self._points if self._can_remove(p)}
        self._value = self._get_value(len(self._points), self._triangles)

    def _get_value(self, points_n, triangles):
        if len(triangles) == 0:
            return 0

        area = sum(t.area for t in triangles)
        max_area = points_n / self._minimal_point_density

        if area <= max_area:
            return area

        area = 0
        for t in sorted(triangles, key=lambda t: t.area):
            if area + t.area <= max_area:
                area += t.area
            else:
                area -= t.area

        return area

    def value_with_added(self, point):
        triangles = self._triangles.union(
            t for t in self._delaunay.triangles_by_points[point] if t.points.issubset(self._points))

        return self._get_value(len(self._points) + 1, triangles)

    def value_with_removed(self, point):
        triangles = self._triangles - self._delaunay.triangles_by_points[point]

        return self._get_value(len(self._points) - 1, triangles)

    @property
    def points_to_add(self):
        return self._points_to_add

    @property
    def points_to_remove(self):
        return self._points_to_remove

    @property
    def value(self):
        return self._value

    @property
    def points(self):
        return self._points

    @property
    def has_minimal_density(self):
        return len(self._points) >= self._minimal_point_density * self._area

    @property
    def area(self):
        return self._area
