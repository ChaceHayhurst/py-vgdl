from vgdl.util.robotplay.RobotPlay import runGame
from vgdl.util.robotplay.Agent import Agent
import time

class MyAgent(Agent):

    def __init__(self):
        self.i = 0

    def getAction(self, state, reward, possible_actions, env):
        time.sleep(0.2)
        self.i+= 1
        env.render()
        if (0<self.i and self.i<7):
            return 0
        return 3

        



runGame(MyAgent(), "C:/Users/Chace/Documents/GitHub/VGDL Tasks/VGDLTask1_lv1.txt", observer='vgdl.state.ColorObserver')