from collections import OrderedDict

from vgdl.core import BasicGame, BasicGameLevel
from vgdl.ontology import GridPhysics
from vgdl.tools import PrettyDict
import math
import copy
import numpy as np
from shapely.geometry import Polygon, LineString

class Observation:
    def as_array(self):
        raise NotImplemented()


class KeyValueObservation(PrettyDict, OrderedDict, Observation):
    """
    Currently a glorified dictionary that keeps its contents in the order it's
    received them. For that reason, it is crucial that values are always passed
    in in the same order, as there is currently no other way to enforce order.
    """

    def as_array(self):
        return np.array(list(self.values()))

    def as_dict(self):
        return self

    def __iter__(self):
        for el in self.values():
            yield el

    def __hash__(self):
        return hash(tuple(self.items()))

    def merge(self, other):
        out = copy.deepcopy(self)
        out.update(other)
        return out


class StateObserver:
    def __init__(self, game: BasicGame) -> None:
        self.set_game(game)

#     @property
#     def game(self):
#         import ipdb; ipdb.set_trace()
#         return self._game

#     @game.setter
#     def game(self, game):
#         print('>>>>>>>')
#         self._game = game

    def get_observation(self) -> Observation:
        return KeyValueObservation()

    def _rect_to_pos(self, r):
        return r.left // self.game.block_size, r.top // self.game.block_size

    @property
    def observation_shape(self):
        obs = self.get_observation()
        shape = obs.as_array().shape
        return shape

    @property
    def observation_length(self):
        obs = self.get_observation()
        length = len(obs.as_array())
        return length

    def set_game(self, game):
        self.game = game

    def __repr__(self):
        return self.__class__.__name__

    def __getstate__(self):
        state = vars(self).copy()
        state.pop('game', None)
        return state


class AbsoluteObserver(StateObserver):
    """
    - Assumes a single-avatar grid physics game
    - Observation is (x, y) of avatar's rectangle, in pixels
    """

    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)

        avatar = game.sprite_registry.get_avatar()
        assert issubclass(avatar.physicstype, GridPhysics)

    def get_observation(self) -> Observation:
        obs = super().get_observation()
        avatar = self.game.sprite_registry.get_avatar()
        obs = obs.merge(KeyValueObservation(x=avatar.rect.left, y=avatar.rect.top))
        return obs


class AbsoluteGridObserver(StateObserver):
    """
    TODO: This is actually deprecated, get rid of it.
    - Assumes a single-avatar grid physics game
    - Observation is (x, y) of avatar converted to grid (not raw pixels)
    """

    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)

        avatars = game.get_sprites('avatar')
        assert len(avatars) == 1, 'Single avatar'
        avatar = avatars[0]
        assert issubclass(avatar.physicstype, GridPhysics)

    def get_observation(self) -> Observation:
        avatars = self.game.get_avatars()
        assert avatars
        position = self._rect_to_pos(avatars[0].rect)
        observation = KeyValueObservation(x=position[0], y=position[1])
        return observation


class OrientationObserver(StateObserver):
    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)
        from vgdl.ontology import OrientedAvatar
        avatar = game.sprite_registry.get_avatar()
        assert isinstance(avatar, OrientedAvatar)

    def get_observation(self):
        obs = super().get_observation()
        avatar = self.game.sprite_registry.get_avatar()
        obs = obs.merge(KeyValueObservation({
            'orientation.x': avatar.orientation[0],
            'orientation.y': avatar.orientation[1],
        }))
        return obs


class ResourcesObserver(StateObserver):
    def __init__(self, game: BasicGameLevel) -> None:
        super().__init__(game)
        # TODO verify it's a resource avatar

    def get_observation(self):
        obs = super().get_observation()
        avatar = self.game.sprite_registry.get_avatar()
        resources = { key: avatar.resources.get(key, 0) for key in self.game.domain.notable_resources }
        obs = obs.merge(KeyValueObservation(resources))
        return obs


class UltrasonicObserver(StateObserver):

    def _get_distance(self, s1, s2):
        return (s1.rect.x - s2.rect.x, s1.rect.y - s2.rect.y)

    def collidesY(self, avatar, sprite, game):
        ATL, ATR, ABL, ABR = (avatar.rect.topleft, avatar.rect.topright, avatar.rect.bottomleft, avatar.rect.bottomright)
        STL, STR, SBL, SBR = (sprite.rect.topleft, sprite.rect.topright, sprite.rect.bottomleft, sprite.rect.bottomright)

        ATL = (ATL[0], -ATL[1])
        ATR = (ATR[0], -ATR[1])
        ABL = (ABL[0], -ABL[1])
        ABR = (ABR[0], -ABR[1])
        STL = (STL[0], -STL[1])
        STR = (STR[0], -STR[1])
        SBL = (SBL[0], -SBL[1])
        SBR = (SBR[0], -SBR[1])

        mod = game.height*game.block_size

        line1 = LineString([(ATL[0], 0), (ATL[0], -mod)])
        line2 = LineString([(ATR[0], 0), (ATR[0], -mod)])
        sprite = Polygon([STL, STR, SBL, SBR])

        if(line1.intersects(sprite)):
            return True
        elif(line2.intersects(sprite)):
            return True
        
        return False
        
    def collidesX(self, avatar, sprite, game):
        ATL, ATR, ABL, ABR = (avatar.rect.topleft, avatar.rect.topright, avatar.rect.bottomleft, avatar.rect.bottomright)
        STL, STR, SBL, SBR = (sprite.rect.topleft, sprite.rect.topright, sprite.rect.bottomleft, sprite.rect.bottomright)

        ATL = (ATL[0], -ATL[1])
        ATR = (ATR[0], -ATR[1])
        ABL = (ABL[0], -ABL[1])
        ABR = (ABR[0], -ABR[1])
        STL = (STL[0], -STL[1])
        STR = (STR[0], -STR[1])
        SBL = (SBL[0], -SBL[1])
        SBR = (SBR[0], -SBR[1])

        mod = game.width*game.block_size

        line1 = LineString([(ATL[1], 0), (ATL[1], mod)])
        line2 = LineString([(ATR[1], 0), (ATR[1], mod)])
        sprite = Polygon([STL, STR, SBL, SBR])

        if(line1.intersects(sprite)):
            return True
        elif (line2.intersects(sprite)):
            return True
        
        return False

    def get_observation(self):
        avatars = self.game.get_avatars()
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        sprites = self.game.sprite_registry.sprites()
        #Initializes walls as farthest points
        closestleft = avatar.rect.x
        closestright = self.game.width*self.game.block_size - avatar.rect.x
        closestbottom = self.game.height*self.game.block_size - avatar.rect.y
        closesttop = avatar.rect.y

        for sprite in sprites:
            if(sprite.id.split('.')[0] != 'background' and sprite.id.split('.')[0] != 'avatar'):

                t1 = self.collidesX(avatar, sprite, self.game) or self.collidesX(sprite, avatar, self.game)
                t2 = self.collidesY(avatar, sprite, self.game) or self.collidesY(sprite, avatar, self.game)

                if(t1):
                    print(sprite.id)
                    if(sprite.rect.y>avatar.rect.y and abs(sprite.rect.y-avatar.rect.y)<closestbottom
                        and abs(sprite.rect.y-avatar.rect.y) != 0):
                        closestbottom = abs(sprite.rect.y-avatar.rect.y)
                
                    if(sprite.rect.y<avatar.rect.y and abs(sprite.rect.y-avatar.rect.y)<closesttop
                        and abs(sprite.rect.y-avatar.rect.y) != 0):
                        closesttop = abs(sprite.rect.y-avatar.rect.y)
                
                if(t2):
                    print(sprite.id)
                    if(sprite.rect.x>avatar.rect.x and abs(sprite.rect.x-avatar.rect.x)<closestright 
                        and abs(sprite.rect.x-avatar.rect.x) != 0):
                        closestright = abs(sprite.rect.x-avatar.rect.x)
                
                    if(sprite.rect.x<avatar.rect.x and abs(sprite.rect.x-avatar.rect.x)<closestleft 
                        and abs(sprite.rect.x-avatar.rect.x) != 0):
                        closestleft = abs(sprite.rect.x-avatar.rect.x)

        obs = KeyValueObservation(
            left = closestleft, right=closestright, top=closesttop, bottom = closestbottom
        )
        return obs


class ColorObserver(StateObserver):

    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)
        self.vocab = {}
        self.curId = 0

    def _get_distance(self, s1, s2):
        return math.hypot(s1.rect.x - s2.rect.x, s1.rect.y - s2.rect.y)

    def get_observation(self):
        avatars = self.game.get_avatars()
        assert avatars
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        sprites = self.game.sprite_registry.sprites()
        DistVar = (self.game.width*self.game.block_size+self.game.height*self.game.block_size)*0.1
        types = []
        positions = []

        for sprite in sprites:
            if(sprite.id.split('.')[0] != 'background' and sprite.id.split('.')[0] != 'avatar'):
                name = sprite.id.split('.')[0]

                if not name in self.vocab:
                    self.vocab[name] = self.curId
                    self.curId+= 1
                
                if(self._get_distance(avatar, sprite) < DistVar):
                    types.append(self.vocab[name])
                    positions.append((sprite.rect.x-avatar.rect.x, sprite.rect.y - avatar.rect.y))
                

        obs = KeyValueObservation(
            types = types, positions = positions
        )
        return obs

class CombinedObserver(StateObserver):

    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)
        self.vocab = {}
        self.curId = 0

    def _get_distance(self, s1, s2):
        return math.hypot(s1.rect.x - s2.rect.x, s1.rect.y - s2.rect.y)

    def collidesY(self, avatar, sprite):
        ATL, ATR, ABL, ABR = (avatar.rect.topleft, avatar.rect.topright, avatar.rect.bottomleft, avatar.rect.bottomright)
        STL, STR, SBL, SBR = (sprite.rect.topleft, sprite.rect.topright, sprite.rect.bottomleft, sprite.rect.bottomright)


        if((ATR[1]>= STL[1] and ABR[1]<= STL[1]) or (ATR[1]>= STR[1] and ABR[1]<= STR[1]) or (ATR[1]>= SBL[1] and ABR[1]<= SBL[1])
            or (ATR[1]>= SBR[1] and ABR[1]<= SBR[1])):
            return True
        
        return False
        
    def collidesX(self, avatar, sprite):
        ATL, ATR, ABL, ABR = (avatar.rect.topleft, avatar.rect.topright, avatar.rect.bottomleft, avatar.rect.bottomright)
        STL, STR, SBL, SBR = (sprite.rect.topleft, sprite.rect.topright, sprite.rect.bottomleft, sprite.rect.bottomright)

        if((ATL[0] <= STL[0] and ATR[0]>= STL[0]) or (ATL[0] <= STR[0] and ATR[0]>= STR[0]) or (ATL[0] <= SBL[0] and ATR[0]>= SBL[0])
            or (ATL[0] <= SBR[0] and ATR[0]>= SBR[0])):
            return True
        
        return False

    def get_observation(self):
        avatars = self.game.get_avatars()
        assert avatars
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        sprites = self.game.sprite_registry.sprites()
        DistVar = (self.game.width*self.game.block_size+self.game.height*self.game.block_size)*0.1
        types = []
        positions = []

        for sprite in sprites:
            if(sprite.id.split('.')[0] != 'background' and sprite.id.split('.')[0] != 'avatar'):
                name = sprite.id.split('.')[0]

                if not name in self.vocab:
                    self.vocab[name] = self.curId
                    self.curId+= 1
                
                if(self._get_distance(avatar, sprite) < DistVar):
                    types.append(self.vocab[name])
                    positions.append((sprite.rect.x-avatar.rect.x, sprite.rect.y - avatar.rect.y))
                
                avatars = self.game.get_avatars()
        assert avatars
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        sprites = self.game.sprite_registry.sprites()
        #Initializes walls as farthest points
        closestleft = avatar.rect.x
        closestright = self.game.width*self.game.block_size - avatar.rect.x
        closestbottom = self.game.height*self.game.block_size - avatar.rect.y
        closesttop = avatar.rect.y

        for sprite in sprites:
            if(sprite.id.split('.')[0] != 'background' and sprite.id.split('.')[0] != 'avatar'):
                t1 = self.collidesX(avatar, sprite) or self.collidesX(sprite, avatar)
                t2 = self.collidesY(avatar, sprite) or self.collidesY(sprite, avatar)

                if(t1):
                    if(sprite.rect.y>avatar.rect.y and abs(sprite.rect.y-avatar.rect.y)<closestbottom
                        and abs(sprite.rect.y-avatar.rect.y) != 0):
                        closestbottom = abs(sprite.rect.y-avatar.rect.y)
                
                    if(sprite.rect.y<avatar.rect.y and abs(sprite.rect.y-avatar.rect.y)<closesttop
                        and abs(sprite.rect.y-avatar.rect.y) != 0):
                        closesttop = abs(sprite.rect.y-avatar.rect.y)
                
                if(t2):
                    if(sprite.rect.x>avatar.rect.x and abs(sprite.rect.x-avatar.rect.x)<closestright 
                        and abs(sprite.rect.x-avatar.rect.x) != 0):
                        closestright = abs(sprite.rect.x-avatar.rect.x)
                
                    if(sprite.rect.x<avatar.rect.x and abs(sprite.rect.x-avatar.rect.x)<closestleft 
                        and abs(sprite.rect.x-avatar.rect.x) != 0):
                        closestleft = abs(sprite.rect.x-avatar.rect.x)

        obs = KeyValueObservation(
            left = closestleft, right=closestright, top=closesttop, bottom = closestbottom, types = types, positions = positions
        )
        
        return obs
    


class PerfectObserver(StateObserver):

    def __init__(self, game: BasicGame) -> None:
        super().__init__(game)
        self.vocab = {}
        self.curId = 0

    def get_observation(self):
        avatars = self.game.get_avatars()
        assert avatars
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        sprites = self.game.sprite_registry.sprites()
        types = []
        positions = []

        for sprite in sprites:
            if(sprite.id.split('.')[0] != 'background' and sprite.id.split('.')[0] != 'avatar'):
                name = sprite.id.split('.')[0]

                if not name in self.vocab:
                    self.vocab[name] = self.curId
                    self.curId+= 1
                
                types.append(self.vocab[name])
                positions.append((sprite.rect.x-avatar.rect.x, sprite.rect.y - avatar.rect.y))
                

        obs = KeyValueObservation(
            types = types, positions = positions
        )
        return obs