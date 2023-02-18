from turtle import Screen
from paddle import Paddle
from ball import Ball
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=800, height=600)
screen.bgcolor('black')
screen.title('Pong')
screen.tracer(0)

pad1 = Paddle(-350, 0)
pad2 = Paddle(350, 0)
ball = Ball()
sb = Scoreboard()

screen.listen()
screen.onkeypress(pad1.go_up, "w")
screen.onkeypress(pad1.go_down, "s")
screen.onkeypress(pad2.go_up, "Up")
screen.onkeypress(pad2.go_down, "Down")

game_is_on = True
while game_is_on:
    screen.update()
    ball.move()

    if ball.ycor() > 290 or ball.ycor() < -290:
        ball.bounce_y()

    if ball.distance(pad1) < 50 and ball.xcor() < -330:
        ball.bounce_x1()

    if ball.distance(pad2) < 50 and ball.xcor() > 330:
        ball.bounce_x2()

    if ball.xcor() > 380:
        ball.reset_position()
        sb.point1()

    if ball.xcor() < -380:
        ball.reset_position()
        sb.point2()

screen.exitonclick()