from vgdl.util.robotplay.RobotPlay import runGame
from vgdl.util.robotplay.Agent import Agent
import time

class MyAgent(Agent):

    def __init__(self):
        self.i = 0

    def getAction(self, state, reward, possible_actions, env):
        time.sleep(0.5)
        self.i+= 1
        env.render()
        if (0<self.i and self.i<6):
            return 2
        if (5<self.i and self.i<10):
            return 1
        return 3

        



runGame(MyAgent(), "C:/Users/Chace/Documents/GitHub/VGDL Tasks/VGDLTask2_lv1.txt", observer='vgdl.state.PerfectObserver', prob=0.75)