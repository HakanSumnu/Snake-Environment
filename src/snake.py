import pyglet as pg
from queue import Queue
import numpy as np
import random

class Snake(pg.window.Window):
    snakeEntities = {"empty": 0, "body": 1, "food": 2}
    snakeDirections = {"none": 0, "left": 1, "up": 2, "right": 3, "down": 4}

    def __init__(self, mapWidth: int = 21, mapHeight: int = 21, windowWidth: int = 600, windowHeight: int = 600, windowCaption: str = "Snake Game", blockMargin: int = 0, visible: bool = True):
        super().__init__(windowWidth, windowHeight, windowCaption, visible=visible)
        self.windowWidth: int = windowWidth
        self.windowHeight: int = windowHeight
        self.windowCaption: str = windowCaption
        self.mapWidth: int = mapWidth
        self.mapHeight: int = mapHeight
        self.blockMargin = blockMargin

        self.tail: Queue = Queue(maxsize=mapWidth * mapHeight)
        self.map: np.matrix = np.zeros((mapHeight, mapWidth), np.uint8)
        self.emptySpaces: np.array = np.zeros((mapHeight,), dtype=np.int32)
        self.emptySpaces.fill(mapWidth)

        self.directionMap = np.empty((mapHeight, mapWidth), dtype=np.uint8)
        self.directionMap.fill(Snake.snakeDirections["none"])

        self.headRow: int = mapHeight // 2
        self.headCol: int = mapWidth // 2
        self.tail.put((self.headRow, self.headCol))
        self.map[self.headRow, self.headCol] = Snake.snakeEntities["body"]
        self.emptySpaces[self.headRow] -= 1

        self.foodRow: int = 0
        self.foodCol: int = 0
        self.put_food()

        self.prevDirection = Snake.snakeDirections["right"]
        self.currentDirection = Snake.snakeDirections["right"]

        self.foodCollected = False
        self.gameOver = False
        self.gameFinished = False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == pg.window.key.LEFT and self.prevDirection != Snake.snakeDirections["right"]:
            self.currentDirection = Snake.snakeDirections["left"]
        elif symbol == pg.window.key.UP and self.prevDirection != Snake.snakeDirections["down"]:
            self.currentDirection = Snake.snakeDirections["up"]
        elif symbol == pg.window.key.RIGHT and self.prevDirection != Snake.snakeDirections["left"]:
            self.currentDirection = Snake.snakeDirections["right"]
        elif symbol == pg.window.key.DOWN and self.prevDirection != Snake.snakeDirections["up"]:
            self.currentDirection = Snake.snakeDirections["down"]

    def on_draw(self) -> None:
        self.clear()
        rect = pg.shapes.Rectangle(0, 0, self.windowWidth / self.mapWidth - self.blockMargin * 2, self.windowHeight / self.mapHeight - self.blockMargin * 2)
        for row in range(self.mapHeight):
            rect.y = (self.mapHeight - 1 - row) * (self.windowHeight / self.mapHeight) + self.blockMargin
            for col in range(self.mapWidth):
                if self.map[row, col] == Snake.snakeEntities["empty"]:
                    continue
                rect.x = col * (self.windowWidth / self.mapWidth) + self.blockMargin
                if self.map[row, col] == Snake.snakeEntities["body"]:
                    rect.color = (255, 0, 0)
                elif self.map[row, col] == Snake.snakeEntities["food"]:
                    rect.color = (0, 255, 0)
                rect.draw()

    def turn(self, action: int):
        if action == Snake.snakeDirections["left"] and self.prevDirection != Snake.snakeDirections["right"]:
            self.currentDirection = action
        elif action == Snake.snakeDirections["up"] and self.prevDirection != Snake.snakeDirections["down"]:
            self.currentDirection = action
        elif action == Snake.snakeDirections["right"] and self.prevDirection != Snake.snakeDirections["left"]:
            self.currentDirection = action
        elif action == Snake.snakeDirections["down"] and self.prevDirection != Snake.snakeDirections["up"]:
            self.currentDirection = action

    def put_food(self) -> None:
        randomNumber = random.randint(1, self.mapWidth * self.mapHeight - self.tail.qsize())

        for row in range(self.mapHeight):
            if randomNumber > self.emptySpaces[row]:
                randomNumber -= self.emptySpaces[row]
            else:
                break

        for col in range(self.mapWidth):
            randomNumber -= (self.map[row, col] == Snake.snakeEntities["empty"])
            if randomNumber == 0:
                self.map[row, col] = Snake.snakeEntities["food"]
                self.emptySpaces[row] -= 1
                self.foodRow = row
                self.foodCol = col
                break

    def reset(self) -> None:
        self.headRow: int = self.mapHeight // 2
        self.headCol: int = self.mapWidth // 2

        self.tail.queue.clear()
        self.tail.put((self.headRow, self.headCol))

        self.map.fill(0)
        self.map[self.headRow, self.headCol] = Snake.snakeEntities["body"]

        self.emptySpaces.fill(self.mapWidth)
        self.emptySpaces[self.headRow] -= 1

        self.directionMap.fill(Snake.snakeDirections["none"])

        self.foodRow: int = 0
        self.foodCol: int = 0
        self.put_food()

        self.prevDirection = Snake.snakeDirections["right"]
        self.currentDirection = Snake.snakeDirections["right"]

        self.foodCollected = False
        self.gameOver = False
        self.gameFinished = False

    def step(self):
        self.prevDirection = self.currentDirection
        self.foodCollected = False

        self.directionMap[self.headRow, self.headCol] = self.currentDirection

        if self.currentDirection == Snake.snakeDirections["left"]:
            self.headCol -= 1
        elif self.currentDirection == Snake.snakeDirections["up"]:
            self.headRow -= 1
        elif self.currentDirection == Snake.snakeDirections["right"]:
            self.headCol += 1
        elif self.currentDirection == Snake.snakeDirections["down"]:
            self.headRow += 1
        
        if self.headRow < 0 or self.headRow >= self.mapHeight or self.headCol < 0 or self.headCol >= self.mapWidth:
            self.tail.put((self.headRow, self.headCol))
            (tailEndRow, tailEndCol) = self.tail.get()
            self.map[tailEndRow, tailEndCol] = Snake.snakeEntities["empty"]
            self.emptySpaces[tailEndRow] += 1
            self.directionMap[tailEndRow, tailEndCol] = Snake.snakeDirections["none"]
            self.gameOver = True
            pg.app.exit()
            return

        if self.map[self.headRow, self.headCol] == Snake.snakeEntities["empty"]:
            self.tail.put((self.headRow, self.headCol))
            self.map[self.headRow, self.headCol] = Snake.snakeEntities["body"]
            self.emptySpaces[self.headRow] -= 1
            (tailEndRow, tailEndCol) = self.tail.get()
            self.map[tailEndRow, tailEndCol] = Snake.snakeEntities["empty"]
            self.emptySpaces[tailEndRow] += 1
            self.directionMap[tailEndRow, tailEndCol] = Snake.snakeDirections["none"]

        elif self.map[self.headRow, self.headCol] == Snake.snakeEntities["body"]:
            self.tail.put((self.headRow, self.headCol))
            (tailEndRow, tailEndCol) = self.tail.get()
            self.map[tailEndRow, tailEndCol] = Snake.snakeEntities["empty"]
            self.emptySpaces[tailEndRow] += 1
            self.directionMap[tailEndRow, tailEndCol] = Snake.snakeDirections["none"]
            self.gameOver = True
            pg.app.exit()
            return

        elif self.map[self.headRow, self.headCol] == Snake.snakeEntities["food"]:
            self.foodCollected = True
            self.tail.put((self.headRow, self.headCol))
            self.map[self.headRow, self.headCol] = Snake.snakeEntities["body"]
            #self.emptySpaces[self.headRow] -= 1
            if self.mapHeight * self.mapWidth != self.tail.qsize():
                self.put_food()
            else:
                self.gameFinished = True
                pg.app.exit()

    def is_done(self):
        return self.gameOver or self.gameFinished

    def run(self, FPS):
        pg.clock.schedule_interval(lambda dt: self.step(), 1.0 / FPS)
        pg.app.run(1.0 / FPS)