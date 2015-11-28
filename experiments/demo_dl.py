from game_manager import GameManager
from agents import DLAgent

agent = DLAgent(10)
gm = GameManager("space_invaders.bin", agent, 'results/testbed3',
                 remove_old_results_dir=True, use_minimal_action_set=True, visualise='rgb')
gm.run(n_episodes=5)
