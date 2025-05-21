import gymnasium as gym
import numpy as np
import random
import pickle
from snake import Snake

class SnakeEnvironmentWrapper(gym.Env):
    def __init__(self, mapWidth: int = 21, mapHeight: int = 21, windowWidth: int = 600, windowHeight: int = 600, windowCaption: str = "Snake Environment", blockMargin: int = 0, foodDirected: bool = True, renderMode = None):
        visible = renderMode == "human"
        self.env = Snake(mapWidth, mapHeight, windowWidth, windowHeight, windowCaption, blockMargin, visible)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(mapHeight * 6, mapWidth), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(4, start=0)
        self.state = np.empty((mapHeight * 6, mapWidth), dtype=np.uint8)
        self.render_mode = renderMode
        self.foodDirected: bool = foodDirected
        self.metadata["render_modes"] = [None, "human"]
        self.timeStepLimit: int = mapWidth * mapHeight
        self.timeStep: int = 0
        self.totalNumberOfFoodsCollected: int = 0

    def get_state(self):
        self.state[:self.env.mapHeight, :] = self.env.map == Snake.snakeEntities["body"]
        self.state[self.env.mapHeight:self.env.mapHeight * 2, :] = self.env.map == Snake.snakeEntities["food"]
        self.state[self.env.mapHeight * 2:self.env.mapHeight * 3, :] = self.env.directionMap == Snake.snakeDirections["left"]
        self.state[self.env.mapHeight * 3:self.env.mapHeight * 4, :] = self.env.directionMap == Snake.snakeDirections["up"]
        self.state[self.env.mapHeight * 4:self.env.mapHeight * 5, :] = self.env.directionMap == Snake.snakeDirections["right"]
        self.state[self.env.mapHeight * 5:self.env.mapHeight * 6, :] = self.env.directionMap == Snake.snakeDirections["down"]
        return np.copy(self.state)

    def get_reward(self):
        reward: float = 0.0
        
        if self.foodDirected == True:
            if self.env.currentDirection == self.env.snakeDirections["left"]:
                if self.env.foodCol - self.env.headCol <= 0:
                    reward = 1.0
                else:
                    reward = -1.0

            elif self.env.currentDirection == self.env.snakeDirections["up"]:
                if self.env.foodRow - self.env.headRow <= 0:
                    reward = 1.0
                else:
                    reward = -1.0
            elif self.env.currentDirection == self.env.snakeDirections["right"]:
                if self.env.foodCol - self.env.headCol >= 0:
                    reward = 1.0
                else:
                    reward = -1.0
            elif self.env.currentDirection == self.env.snakeDirections["down"]:
                if self.env.foodRow - self.env.headRow >= 0:
                    reward = 1.0
                else:
                    reward = -1.0

            #reward /= (self.totalNumberOfFoodsCollected + 1) ** (0.5)
            reward *= max(0, (20000 - self.totalNumberOfFoodsCollected) / 20000)

        if self.env.gameFinished == True:
            reward = 10.0

        elif self.env.foodCollected == True:
            reward = 1.0
            self.totalNumberOfFoodsCollected += 1

        elif self.env.gameOver == True:
            reward = -1.0

        else:
            reward -= 0.366 / (self.env.mapWidth * self.env.mapHeight)

        return reward

    def get_info(self):
        return {"length": self.env.tail.qsize()}

    def reset(self, seed=None):
        super().reset(seed=seed)
        random.seed(seed)
        self.env.reset()
        self.timeStep = 0
        self.timeStepLimit = self.env.mapWidth * self.env.mapHeight
        return self.get_state(), self.get_info()

    def step(self, action: int):
        self.env.turn(action + 1)
        self.env.step()
        self.timeStep += 1
        if self.env.foodCollected:
            self.timeStep = 0
        if self.render_mode == "human":
            self.env.switch_to()
            self.env.dispatch_events()
            self.env.on_draw()
            self.env.flip()
        return self.get_state(), self.get_reward(), self.env.is_done(), self.timeStep == self.timeStepLimit, self.get_info()

    def render(self):
        return None

    def save(self, path):
        with open(path, 'wb') as file:
            file.write(self.totalNumberOfFoodsCollected.to_bytes(4, 'big'))

    def load(path = None, mapWidth: int = 21, mapHeight: int = 21, windowWidth: int = 600, windowHeight: int = 600, windowCaption: str = "Snake Environment", blockMargin: int = 0, foodDirected: bool = True, renderMode = None):
        if path == None:
            return None

        env = SnakeEnvironmentWrapper(mapWidth, mapHeight, windowWidth, windowHeight, windowCaption, blockMargin, foodDirected, renderMode)
        with open(path, 'rb') as file:
            env.totalNumberOfFoodsCollected = int.from_bytes(file.read(4), "big")

        return env

    def close(self):
        self.env.close()