from vgdl.util.robotplay.RobotPlay import runGame
from vgdl.util.robotplay.Agent import Agent
import time

class MyAgent(Agent):

    def __init__(self):
        self.i = 0

    def getAction(self, state, reward, possible_actions):
        time.sleep(1)
        self.i+= 1
        if(0<self.i and self.i <6):
            return 0
        if(6<=self.i and self.i<15):
            return 3
        if(self.i == 15):
            return 1
        if(15<self.i and self.i<18):
            return 3
        if(self.i>=18):
            return 5
        



runGame(MyAgent(), "C:/Users/Chace/Documents/GitHub/VGDL Tasks/VGDLTask1_lv1.txt", observer='vgdl.state.UltrasonicObserver')