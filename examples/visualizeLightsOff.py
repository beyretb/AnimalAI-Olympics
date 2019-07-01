from animalai.envs.environment import UnityEnvironment
from animalai.envs.arena_config import ArenaConfig
import random
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

env_path = '../env/AnimalAI'
worker_id = random.randint(1, 100)

seed = 10
base_port = 5005
sub_id = 1
run_id = 'train_example'
run_seed = 1
docker_target_name = None
no_graphics = False
n_arenas = 4
resolution = 128

if env_path is not None:
    env_path = (env_path.strip()
                .replace('.app', '')
                .replace('.exe', '')
                .replace('.x86_64', '')
                .replace('.x86', ''))
docker_training = docker_target_name is not None

env = UnityEnvironment(
    n_arenas=n_arenas,
    file_name=env_path,
    worker_id=worker_id,
    seed=seed,
    docker_training=docker_training,
    play=False,
    resolution=resolution
)

arena_config_in = ArenaConfig('configs/7-InternalMemory.yaml')
env.reset(arenas_configurations=arena_config_in)
fig, axes = plt.subplots(2, 2)
imshows = []
for i in range(2):
    for j in range(2):
        axes[i, j].set_title('Arena ' + str(i * 2 + j))
        axes[i, j].axis('off')
        imshows.append(axes[i, j].imshow(np.zeros((resolution, resolution, 3))))


def initialize_animation():
    for i in range(4):
        imshows[i].set_data(np.zeros((resolution, resolution, 3)))


def run_step_imshow(step):
    res = env.step(np.random.randint(0, 3, size=2 * n_arenas))
    for i in range(4):
        imshows[i].set_data(res['Learner'].visual_observations[0][i, :, :, :])
    fig.suptitle('Step = ' + str(step))
    return imshows


try:
    anim = animation.FuncAnimation(fig, run_step_imshow, init_func=initialize_animation, frames=100, interval=50)
    plt.show()
except KeyboardInterrupt:
    env.close()
