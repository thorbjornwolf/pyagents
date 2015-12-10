from game_manager import GameManager
from agents import SarsaAgent

agent = SarsaAgent(n_frames_per_action=10,
                   trace_type='replacing', 
                   learning_rate=0.01, 
                   discount=0.99, 
                   lambda_v=0.5)

gm = GameManager("pong.bin",
                 agent, 'results/testbed3',
                 remove_old_results_dir=True, use_minimal_action_set=True, 
                 visualise=None)
                 # visualise='rgb')

gm.run(n_episodes=500)