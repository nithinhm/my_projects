from turtle import Turtle

MOVE_DISTANCE = 20
START_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0


class Snake:

    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]

    def create_snake(self):
        for position in START_POSITIONS:
            self.append_segment(position)

    def append_segment(self, pos):
        seg = Turtle('square')
        seg.color('white')
        seg.penup()
        seg.goto(pos)
        self.segments.append(seg)

    def extend(self):
        self.append_segment(self.segments[-1].position())

    def move(self):
        for s_num in range(len(self.segments) - 1):
            new_x = self.segments[len(self.segments) - s_num - 2].xcor()
            new_y = self.segments[len(self.segments) - s_num - 2].ycor()
            self.segments[len(self.segments) - s_num - 1].goto(new_x, new_y)
        self.head.forward(MOVE_DISTANCE)

    def up(self):
        if self.head.heading() != DOWN:
            self.head.setheading(UP)

    def down(self):
        if self.head.heading() != UP:
            self.head.setheading(DOWN)

    def left(self):
        if self.head.heading() != RIGHT:
            self.head.setheading(LEFT)

    def right(self):
        if self.head.heading() != LEFT:
            self.head.setheading(RIGHT)
