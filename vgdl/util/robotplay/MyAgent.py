from vgdl.util.robotplay.RobotPlay import runGame
from vgdl.util.robotplay.Agent import Agent
import time

class MyAgent(Agent):

    def __init__(self):
        self.moveNum = 0
        self.LastState = []
        self.LastMove = 0
        self.goalPos = ()
        self.fired = False
        self.MR = False
        self.ML = False
        self.fire = False

    def getAction(self, state, reward, possible_actions, env):
        time.sleep(0.5)
        moved = self.didMove(state)
        if(not moved and self.LastMove != 4):
            self.LastState = state
            return self.LastMove
        
        self.LastState = state

        #First movements to locate goal spaces on the grid

        if(self.fired==True):
            self.LastMove = 4
            return 4

        if(self.fire == True):
            self.LastMove = 5
            self.fired= True
            return 5

        if(self.MR == True):
            self.fire = True
            self.LastMove = 3
            return 3
        
        if(self.ML == True):
            self.fire == True
            self.LastMove = 2
            return 2

        if(self.moveNum<20 and len(self.goalPos) == 0):
            idList = state[4]
            positions = state[5]

            for i in range(0, len(idList)):
                if(idList[i] == 0):
                    self.goalPos = positions[i]
                    self.LastMove = 4
                    return 4

            if(self.moveNum<2):
                self.moveNum+=1
                self.LastMove = 0
                return 0
            else:
                self.moveNum+=1
                self.LastMove = 3
                return 3
        
        if(self.goalPos[1]< 2.5 and self.goalPos[1]>-2.5):
            if(self.goalPos[0]< 7.5 and self.goalPos[0]>2.5):
                self.LastMove = 2
                self.MR= True
                return 2

            if(self.goalPos[0]> -7.5 and self.goalPos[0]<-2.5):
                self.LastMove = 3
                self.ML = True
                return 3
            
            elif(self.goalPos[0] > 0):
                print("moving right to goal")
                self.goalPos = (self.goalPos[0], self.goalPos[1]-5)
                self.LastMove = 3
                self.fire=True
                return 3
        

            elif(self.goalPos[0] < 0):
                print("moving left to goal")
                self.goalPos = (self.goalPos[0], self.goalPos[1]-5)
                self.LastMove = 2
                self.fire = True
                return 2


        elif(self.goalPos[1] > 2.5):
            print("moving down to goal")
            self.goalPos = (self.goalPos[0], self.goalPos[1]-5)
            self.LastMove = 1
            return 1
        elif(self.goalPos[1] < -2.5):
            self.goalPos = (self.goalPos[0], self.goalPos[1]+5)
            print("moving up to goal")
            self.LastMove = 0
            return 0







        

    



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
        
        if(not vals<0.10 == False):
            print('didnt move')
            return False
        else:
            print('moved')
            return True



        

        



runGame(MyAgent(), "C:/Users/Chace/Documents/GitHub/VGDL Tasks/VGDLTask1_lv1.txt", observer='vgdl.state.CombinedObserver', prob=0.33)