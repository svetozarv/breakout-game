from tkinter import *
import random
import time
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BALL_RADIUS = 5
BALL_COLOR = "white"

BRICK_WIDTH = 80
BRICK_HEIGHT = 20
BRICKS_ROW_COLORS = ["pink", "red", "orange", "yellow", "green", "blue", "purple"]

PADDLE_WIDTH = 28
PADDLE_HEIGHT = 6
PADDLE_SPEED = 3

GAME_SPEED_MULTIPLIER = 0    #  ex. 0.02 == 2%
SLEEP_TIME = 0.01

BALL_SPEED_MULTIPLIER = 0.5      #  ex. 0.7 == 70%
BALL_MAXSPEED = 2.8284
BALL_MAXSPEED_SQRD = 10


class Game:
    def __init__(self) -> None:
        self.window = Tk()
        self.window.title("Breakout game")
        self.window.minsize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.canvas = Canvas(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.ball: Ball = None
        self.paddle: Paddle = None
        self.bricks = self.brick_wall()
        self.score = 0
        self.delay = SLEEP_TIME
        self.score_canvas = Canvas(width=SCREEN_WIDTH, height=30, bg="black", highlightthickness=0)
        self.score_canvas.create_text(SCREEN_WIDTH // 2, 15, text=f"Score: {self.score}")


    def brick_wall(self, rows=3, pad_x=8, pad_y=8) -> list:
        # create the brick wall
        bricks = []
        x = pad_x
        y = pad_y
        for color in BRICKS_ROW_COLORS:
            for i in range(0, SCREEN_WIDTH // (pad_x + BRICK_WIDTH)):   # construct a row
                brick = Brick(self.canvas, x, y, color=color)
                bricks.append(brick)
                x += BRICK_WIDTH + pad_x
            x = pad_x
            y += BRICK_HEIGHT + pad_y
        print(f"brick_wall(): {bricks}")
        print(f"bricks len: {len(bricks)}")
        return bricks


    def mainloop(self):
        game_running = True
        while game_running:
            ball.move()
            paddle.move()
            self.score = ball.score
            self.delay = ball.delay
            self.update_score()
            self.canvas.update()
            self.canvas.update_idletasks()
            time.sleep(self.delay)


    def update_score(self):
        pass


class Ball:
    def __init__(self, canvas: Canvas, paddle, bricks: list) -> None:
        self.canvas = canvas
        self.paddle = paddle
        self.bricks = bricks
        self.score = 0
        self.delay = SLEEP_TIME
        # print(f"ball.bricks : {self.bricks}")

        # create a ball in center of screen 
        self.x0 = SCREEN_WIDTH / 2 - BALL_RADIUS
        self.y0 = SCREEN_HEIGHT / 2 - BALL_RADIUS
        self.x1 = SCREEN_WIDTH / 2 + BALL_RADIUS
        self.y1 = SCREEN_HEIGHT / 2 + BALL_RADIUS
        self.id = self.canvas.create_oval(self.x0, self.y0, self.x1, self.y1, fill=BALL_COLOR)
        self.coords = Coords(self.canvas, self.id)

        # make the ball go upward within 120 degrees
        speed_vector = BALL_MAXSPEED
        y_vector_min = BALL_MAXSPEED / 2 * 1.4
        self.goto_y = random.uniform(-y_vector_min, -speed_vector)
        self.goto_x = math.sqrt(BALL_MAXSPEED_SQRD - self.goto_y**2)

    
    def calculate_yspeed(self, a=1):
        x = self.goto_x
        return math.sqrt(BALL_MAXSPEED_SQRD - a*a*x*x)

    def move(self):

        # react to collision with screen edges
        if self.coords.y0 <= 0 or self.coords.y1 >= SCREEN_HEIGHT:
            self.goto_y = -self.goto_y
        elif self.coords.x0 <= 0 or self.coords.x1 >= SCREEN_WIDTH:
            self.goto_x = -self.goto_x

        # react to collision with bricks
        for brick in self.bricks:
            if not brick: continue
            if self.coords.collided_top(brick.coords):
                self.goto_y = -self.goto_y
                self.hit_brick(brick)
            elif self.coords.collided_left(brick.coords) or self.coords.collided_right(brick.coords):
                self.goto_x = -self.goto_x
                self.hit_brick(brick)
            elif self.coords.collided_bottom(brick.coords):
                self.goto_y = -self.goto_y
                self.hit_brick(brick)

        # react to collision with paddle
        if self.coords.collided_bottom(self.paddle.coords):
            
            # paddle speed impact on ball speed
            if self.paddle.goto_x * self.goto_x > 0 or 0 <= self.goto_x <= 0.05 * BALL_MAXSPEED:
                a = BALL_SPEED_MULTIPLIER * (BALL_MAXSPEED - abs(self.goto_x))
                self.goto_x = a + abs(self.goto_x)
                self.goto_x = self.paddle.goto_x
                self.goto_y = self.calculate_yspeed()
            elif self.paddle.goto_x * self.goto_x < 0:
                self.goto_x = BALL_SPEED_MULTIPLIER * self.goto_x 
                self.goto_y = self.calculate_yspeed()
                
            self.goto_y = -self.goto_y
        
        elif self.coords.collided_left(self.paddle.coords) or self.coords.collided_right(self.paddle.coords):
            self.goto_x = -self.goto_x
        elif self.coords.collided_top(self.paddle.coords):
            self.goto_y = -self.goto_y

        self.canvas.move(self.id, self.goto_x, self.goto_y)
        self.coords.update()


    def hit_brick(self, brick):
        brick.destroy()
        self.score += 1
        self.delay = self.delay - self.delay*GAME_SPEED_MULTIPLIER
        self.bricks.remove(brick)
        # i = self.bricks.index(brick)
        # self.bricks[i] = None

class Coords:
    def __init__(self, canvas: Canvas, obj_id) -> None:
        self.canvas = canvas
        self.obj_id = obj_id
        self.x0, self.y0, self.x1, self.y1 = canvas.coords(obj_id)

    def update(self):
        self.x0, self.y0, self.x1, self.y1 = self.canvas.coords(self.obj_id)

    def collided_left(self, other):
        if self.within_y(other) and self.x0 < other.x1 < self.x1:
            return True
        return False
    
    def collided_right(self, other):
        if self.within_y(other) and self.x0 < other.x0 < self.x1:
            return True
        return False
    
    # collision occured at the top of self
    def collided_top(self, other):
        if self.within_x(other) and self.y0 <= other.y1 < self.y1:
            return True
        return False
    
    # collision occured at the bottom of self
    def collided_bottom(self, other):
        if self.within_x(other) and self.y0 < other.y0 <= self.y1:
            return True
        return False
    
    def within_x(self, other):
        if (other.x0 < self.x0 < other.x1) or (other.x0 < self.x1 < other.x1) \
            or (self.x0 < other.x0 < self.x1) or (self.x0 < other.x1 < self.x1):
            return True
        return False

    def within_y(self, other):
        if (other.y0 < self.y0 < other.y1) or (other.y0 < self.y1 < other.y1) \
            or (self.y0 < other.y0 < self.y1) or (self.y0 < other.y1 < self.y1):
            return True
        return False


class Paddle:
    def __init__(self, canvas: Canvas, color="white") -> None:
        self.canvas = canvas
        self.x0 = SCREEN_WIDTH // 2 - PADDLE_WIDTH
        self.y0 = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT + 150
        self.x1 = SCREEN_WIDTH // 2 + PADDLE_WIDTH
        self.y1 = SCREEN_HEIGHT // 2 + PADDLE_HEIGHT + 150
        self.id = self.canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill=color)
        self.coords = Coords(self.canvas, self.id)
        self.goto_x = 0

        self.canvas.bind_all("<KeyPress-Left>", lambda x: self.move_left())
        self.canvas.bind_all("<KeyPress-Right>", lambda x: self.move_right())

    def move(self):
        if self.coords.x0 <= 0:
            self.goto_x = 0
            self.canvas.move(self.id, 1, 0)
        elif self.coords.x1 >= SCREEN_WIDTH:
            self.goto_x = 0
            self.canvas.move(self.id, -1, 0)
        else:
            self.canvas.move(self.id, self.goto_x, 0)
        self.coords.update()

    def move_left(self):
        self.goto_x = -PADDLE_SPEED

    def move_right(self):
        self.goto_x = PADDLE_SPEED


class Brick():
    def __init__(self, canvas: Canvas, x, y, width=BRICK_WIDTH, height=BRICK_HEIGHT, color="white") -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.id = self.canvas.create_rectangle(self.x, self.y, self.x + width, self.y + height, fill=color)
        self.coords = Coords(self.canvas, self.id)
    
    def destroy(self):
        self.canvas.delete(self.id)


game = Game()
paddle = Paddle(game.canvas)
ball = Ball(game.canvas, paddle, game.bricks)
game.ball = ball
game.paddle = paddle
game.mainloop()
