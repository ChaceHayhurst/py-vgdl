from abc import ABCMeta, abstractmethod

class Agent():
    __metaclass__ = ABCMeta

    def __init__():
        pass
    
    @abstractmethod
    def getAction(state, reward, possible_actions):
        pass