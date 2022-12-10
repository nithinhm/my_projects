from turtle import Turtle


class Ball(Turtle):
    def __init__(self):
        super().__init__()
        self.color('white')
        self.shape('circle')
        self.penup()
        self.x_step = 0.1
        self.y_step = 0.1
        self.move_speed = 0.1

    def move(self):
        self.goto(self.xcor() + self.x_step, self.ycor() + self.y_step)

    def bounce_x1(self):
        self.x_step = abs(self.x_step)
        self.move_speed *= 0.9

    def bounce_x2(self):
        self.x_step = -abs(self.x_step)
        self.move_speed *= 0.9

    def bounce_x(self):
        self.x_step *= -1

    def bounce_y(self):
        self.y_step *= -1

    def reset_position(self):
        self.goto(0, 0)
        self.move_speed = 0.1
        self.bounce_x()
