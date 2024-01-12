import turtle
import math

# Point class for projected points
class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # Rotate point around x axis
    def rotate_point_x(self, point, angle):
        r = distance(0, 0, 0, point.x, point.y, point.z)
        x1 = point.x
        y1 = point.y + math.sin(angle) * r
        z1 = point.z + math.cos(angle) * r
        return Point(x1, y1, z1)
    
    # Rotate point around y axis
    def rotate_point_y(self, point, angle):
        r = distance(0, 0, 0, point.x, point.y, point.z)
        x1 = point.x + math.cos(angle) * r
        y1 = point.y
        z1 = point.z + math.sin(angle) * r
        return Point(x1, y1, z1)
    
    # Rotate point around z axis
    def rotate_point_z(self, point, angle):
        r = distance(0, 0, 0, point.x, point.y, point.z)
        x1 = point.x + math.cos(angle) * r
        y1 = point.y + math.sin(angle) * r
        z1 = point.z
        return Point(x1, y1, z1)

    # Rotating point around coordinate origin (0, 0, 0)
    def rotate_point_around_origin(self, ax, ay, az, point = None, return_ = False):
        # If provided a point
        if point:
            p1 = self.rotate_point_x(point, ax)
            p2 = self.rotate_point_y(p1, ay)
            p3 = self.rotate_point_z(p2, az)
            if return_:
                return p3
            else:
                self.x = p3.x
                self.y = p3.y
                self.z = p3.z

        # else use self        
        else:
            p1 = self.rotate_point_x(self, ax)
            p2 = self.rotate_point_y(p1, ay)
            p3 = self.rotate_point_z(p2, az)
            if return_:
                return p3
            else:
                self.x = p3.x
                self.y = p3.y
                self.z = p3.z

    # Rotating point around another point
    def rotate_point_around_point(self, other, ax, ay, az):
        # Coordinate differences to calculate rotation around origin to then translate point to *other* origin
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z

        rpoint = self.rotate_point_around_origin(ax, ay, az, Point(dx, dy, dz), True)
        self.x, self.y, self.z = rpoint.x + other.x, rpoint.y + other.y, rpoint.z + other.z

    # Project self into 2d
    def project(self) -> Point2D:
        if self.z == 0:
            return Point2D(self.x, self.y)
        else:
            projection_factor = 200 / (self.z + (abs(self.z) / self.z) * 1e-16)
            return Point2D(self.x * projection_factor, self.y * projection_factor)
        
def distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

class Object:
    def __init__(self, vertices, edges, faces, position, color, outline_color):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces
        self.position = position
        self.color = color
        self.outline_color = outline_color
        self.ax, self.ay, self.az = 0, 0, 0

    # Sort faces by depth to render in order
    def sort_faces(self):
        def key_(v):
            point = Point(self.vertices[v].x + self.position.x, self.vertices[v].y + self.position.y, self.vertices[v].z + self.position.z)
            point.rotate_point_around_point(self.position, self.ax, self.ay, self.az)
            return point.x, point.y, point.z
        return sorted(self.faces, key = lambda face: sum(distance(*key_(v), 0, 0, 0) for v in face) / len(face), reverse = True)

    def render(self):
        global faces_to_draw
        # Sorts self's faces
        sorted_faces = self.sort_faces()

        for face in sorted_faces:
            # Finds center of the face
            centroid = Point(sum(self.vertices[v].x + self.position.x for v in face) / len(face),
                            sum(self.vertices[v].y + self.position.y for v in face) / len(face),
                            sum(self.vertices[v].z + self.position.z for v in face) / len(face))
            depth = distance(centroid.x, centroid.y, centroid.z, 0, 0, 0)

            # Makes a polygon according to projected face face
            polygon = []
            for v in face:
                point = Point(self.vertices[v].x + self.position.x, self.vertices[v].y + self.position.y, self.vertices[v].z + self.position.z)
                point.rotate_point_around_point(self.position, self.ax, self.ay, self.az)
                polygon.append(point.project())

            # Adds face info to global faces list
            faces_to_draw.append((polygon, depth, self.color, self.outline_color))

# Global drawing function
def draw_objects():
    # Sorts faces by provided depth from furthest to closest
    for face_info in sorted(faces_to_draw, key = lambda face: face[1], reverse = True): # face[1] is depth
        polygon = face_info[0]
        fill_color = face_info[2]
        outline_color = face_info[3]
        turtle.pensize(10)
        turtle.pencolor(outline_color)
        turtle.penup()
        turtle.goto(polygon[0].x, polygon[0].y) # moving to polygon origin
        turtle.pendown()
        for point in polygon: # drawing the polygon's outline
            turtle.goto(point.x, point.y)
        turtle.penup()
        turtle.goto(polygon[0].x, polygon[0].y)
        turtle.begin_poly()
        turtle.begin_fill()
        turtle.fillcolor(fill_color)
        for point in polygon: # drawing the filled polygon
            turtle.goto(point.x, point.y)
        turtle.goto(polygon[0].x, polygon[0].y) # completing the polygon
        turtle.end_poly()
        turtle.end_fill()

# init
screen = turtle.Screen()
screen.bgcolor("black")
turtle.speed(0)

# global
faces_to_draw = []

# initiation of object
vertices = [
    Point(-1, -1, -1),
    Point(1, -1, -1),
    Point(1, 1, -1),
    Point(-1, 1, -1),
    Point(-1, -1, 1),
    Point(1, -1, 1),
    Point(1, 1, 1),
    Point(-1, 1, 1)
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (0, 3, 7, 4),
    (1, 2, 6, 5)
]

obj = Object(vertices, edges, faces, Point(0, 0, 1), "blue", "white")

# rendering the object before globally drawing it
obj.render()

# drawing globally
draw_objects()

turtle.done()