from turtle import Screen
from snake import Snake
from food import Food
from scoreboard import Scoreboard
import time

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor('black')
screen.title('My Snake Game')
screen.tracer(0)
boundary = 295

sk = Snake()
food = Food()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(sk.up, "Up")
screen.onkey(sk.down, "Down")
screen.onkey(sk.left, "Left")
screen.onkey(sk.right, "Right")

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.08)

    sk.move()

    if sk.head.distance(food) < 15:
        food.refresh()
        sk.extend()
        scoreboard.update_score()

    if sk.head.xcor() > boundary or sk.head.xcor() < -boundary or sk.head.ycor() > boundary or sk.head.ycor() < -boundary:
        game_is_on = False
        scoreboard.game_over()

    for segment in sk.segments[1:]:
        if sk.head.distance(segment) < 15:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()
