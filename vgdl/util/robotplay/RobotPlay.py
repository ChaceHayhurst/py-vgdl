import os
import sys
import time
import itertools
import numpy as np
import logging
import gym

import vgdl.interfaces.gym

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def register_vgdl_env(domain_file, level_file, observer=None, blocksize=None):
    from gym.envs.registration import register, registry
    level_name = '.'.join(os.path.basename(level_file).split('.')[:-1])
    env_name = 'vgdl_{}-v0'.format(level_name)

    register(
        id=env_name,
        entry_point='vgdl.interfaces.gym:VGDLEnv',
        kwargs={
            'game_file': domain_file,
            'level_file': level_file,
            'block_size': blocksize,
            'obs_type': observer or 'features',
        },
        nondeterministic=True
    )

    return env_name


def runGame(agent, levelfile, domainfile=None, ontology=None, observer=None, reps=1, blocksize=24, tracedir=None, pause_on_finish=False):


    if ontology is not None:
        import vgdl
        vgdl.registry.register_from_string(ontology)

    if observer is not None:
        import importlib
        name_bits = observer.split('.')
        module_name = '.'.join(name_bits[:-1])
        class_name = name_bits[-1]
        print(module_name)
        print(class_name)
        module = importlib.import_module('vgdl.state')
        observer_cls = getattr(module, 'OneObserver')
    else:
        observer_cls = None

    if domainfile is None:
        # rely on naming convention to figure out domain file
        domainfile = os.path.join(os.path.dirname(levelfile),
                                       os.path.basename(levelfile).split('_')[0] + '.txt')

    env_name = register_vgdl_env(domainfile, levelfile, observer_cls,
                                 blocksize)
    # env_name = '.'.join(os.path.basename(levelfile).split('.')[:-1])

    logging.basicConfig(format='%(levelname)s:%(name)s %(message)s',
            level=logging.DEBUG)

    if tracedir is None:
        tracedir = os.path.join(THIS_DIR, '..', 'traces')
    tracedir = os.path.join(tracedir, env_name)
    os.makedirs(tracedir, exist_ok=True)
    env = gym.make(env_name)

    for epoch_i in range(reps):

        done = False
        state = env._get_obs()
        reward = 0.
        while(not done):
            env.render()
            action = 1
            obs, reward, done, _ = env.step(action)
            print(obs)
    
    env.close()

        



runGame(None, "C:/Users/Chace/Documents/GitHub/py-vgdl/vgdl/games/aliens_lvl0.txt", observer='vgdl.state.OneObserver')




