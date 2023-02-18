import time
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=600, height=600)
screen.tracer(0)

player = Player()
cm = CarManager()
sb = Scoreboard()

screen.listen()
screen.onkeypress(player.move, 'Up')

game_is_on = True
while game_is_on:
    screen.update()

    cm.generate_car()
    cm.move_cars()

    for car in cm.all_cars:
        if car.distance(player) < 20:
            sb.over()
            game_is_on = False

    if player.has_crossed_finish():
        player.go_to_start()
        sb.increase_level()
        cm.level_up()

    time.sleep(0.1)

screen.exitonclick()