from vgdl.util.robotplay.RobotPlay import runGame
from vgdl.util.robotplay.Agent import Agent
import time

class MyAgent(Agent):

    def __init__(self):
        self.moveNum = 0
        self.LastState = []
        self.LastMove = 0
        self.blockPos = ()
        self.goalPos = ()
        self.nextToBlock = False
        self.inPosition = False
        self.j = 0

    def getAction(self, state, reward, possible_actions, env):
        time.sleep(0.5)
        moved = self.didMove(state)
        if(not moved and self.LastMove != 4):
            self.LastState = state
            return self.LastMove
        
        self.LastState = state

        #First movements to locate goal spaces on the grid
        print(self.goalPos)
        print(self.blockPos)
        if(self.moveNum<30 and (len(self.goalPos) == 0 or len(self.blockPos) == 0)):
            idList = state[4]
            positions = state[5]

            for i in range(0, len(idList)):
                if(idList[i] == 0 and len(self.blockPos) == 0):
                    self.blockPos = positions[i]
                if(idList[i] == 1 and len(self.goalPos) == 0):
                    self.goalPos = positions[i]


            if(self.moveNum<4):
                self.moveNum+=1
                self.LastMove = 0
                if(len(self.goalPos) > 0):
                    self.goalPos = (self.goalPos[0], self.goalPos[1] + 5)
                if(len(self.blockPos) > 0):
                    self.blockPos = (self.blockPos[0], self.blockPos[1] + 5)
                return 0
            elif(self.moveNum<8):
                self.moveNum+=1
                self.LastMove = 2
                if(len(self.goalPos) > 0):
                    self.goalPos = (self.goalPos[0]+5, self.goalPos[1])
                if(len(self.blockPos) > 0):
                    self.blockPos = (self.blockPos[0]+5, self.blockPos[1])
                return 2

            elif(self.moveNum<30):
                self.moveNum+=1
                self.LastMove = 3
                if(len(self.goalPos) > 0):
                    self.goalPos = (self.goalPos[0]+5, self.goalPos[1])
                if(len(self.blockPos) > 0):
                    self.blockPos = (self.blockPos[0]+5, self.blockPos[1])
                return 3

        #move to the left of the block
        if(self.nextToBlock == False):
            if(self.blockPos[0] < -2.5 and self.blockPos[0] > -9):

                if(self.blockPos[1] > 2.5):
                    self.LastMove = 1
                    self.goalPos = (self.goalPos[0], self.goalPos[1]-5)
                    self.blockPos = (self.blockPos[0], self.blockPos[1]-5)
                    return 1

                if(self.blockPos[1] < -2.5):
                    self.LastMove = 0
                    self.goalPos = (self.goalPos[0], self.goalPos[1]+5)
                    self.blockPos = (self.blockPos[0], self.blockPos[1]+5)
                    return 0

                if(self.blockPos[1] < 2.5 and self.blockPos[1] > -2.5):
                    self.LastMove = 4
                    self.nextToBlock = True
                    return 4         

            if(self.blockPos[0] > -2.5):
                self.LastMove = 2
                self.goalPos = (self.goalPos[0] + 5, self.goalPos[1])
                self.blockPos = (self.blockPos[0] -5, self.blockPos[1])
                return 2
            
            if(self.blockPos[0] < -7.5):
                self.LastMove = 3
                self.goalPos = (self.goalPos[0] - 5, self.goalPos[1])
                self.blockPos = (self.blockPos[0] + 5, self.blockPos[1])
                return 3
        
        if(self.nextToBlock and not self.inPosition):
            if(self.goalPos[0] < 10):
                self.inPosition = True
                self.LastMove = 4
                return 4
            

            if(self.goalPos[0] > 10):
                self.LastMove = 3
                self.goalPos = (self.goalPos[0] - 5, self.goalPos[1])
                return 3
        
        if(self.inPosition):
            if(self.j == 0):
                self.j+= 1
                self.LastMove = 0
                return 0
            if(self.j == 1):
                self.j+= 1
                self.LastMove = 3
                return 3
            return 1



    def didMove(self, state):
        
        oldstate = self.LastState
        if(len(oldstate) == 0):
            return True
        oldIdList = oldstate[4]
        newIdList = state[4]

        if(not len(oldIdList) == len(newIdList)):
            return True

        for i in range(0, len(oldIdList)):
            if(not oldIdList[i] == newIdList[i]):
                return True
        
        oldPos = oldstate[5]
        newPos = state[5]

        vals = 0

        for i in range(0, len(oldPos)):
            vals+=(oldPos[i][0]-newPos[i][0])
            vals+=(oldPos[i][1]-newPos[i][1])
        
        for i in range(0, 4):
            vals+=(oldstate[i] - state[i])
        
        if(not vals<0.1 == False):
            print('didnt move')
            return False
        else:
            print('moved')
            return True



        

        



runGame(MyAgent(), "C:/Users/Chace/Documents/GitHub/VGDL Tasks/VGDLTask2_lv1.txt", observer='vgdl.state.CombinedObserver', prob=0.9)