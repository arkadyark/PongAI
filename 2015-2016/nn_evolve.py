# Where the magic happens

import os
import pickle

from neat import nn, parallel, population, visualize
from neat.config import Config

games_per_net = 3
num_generations = 50

# Use the neural network phenotype to play some games, and see how fit it is
def evaluate_genome(g):
    # A thought - train the first N generations with a simpler fitness function, like just trying to hit the ball
    # May or may not be necessary

    net = nn.create_feed_forward_phenotype(g)

    fitness = 0.0

    for game in range(games_per_net):
        fitness += 1
        # Play game
        # Get score
        # Add score difference to fitness
        # TODO - switch sides, table size, etc

    # Fitness = average score difference
    return fitness / games_per_net


# Load the config file
local_dir = os.path.dirname(__file__)
config = Config(os.path.join(local_dir, 'nn_config'))

# Evolve over generations
pop = population.Population(config)
pe = parallel.ParallelEvaluator(4, evaluate_genome)
pop.epoch(pe.evaluate, num_generations)


# Save the winner
print('Number of evaluations: ' + str(pop.total_evaluations))
winner = pop.most_fit_genomes[-1]
with open('nn_winner_genome', 'wb') as f:
    pickle.dump(winner, f)

# Display the winner
print(winner)

# Plot the evolution of the best/average fitness.
visualize.plot_stats(pop, ylog=True, filename="nn_fitness.svg")
# Visualizes speciation
visualize.plot_species(pop, filename="nn_speciation.svg")
# Visualize the best network.
visualize.draw_net(winner, view=True, filename="nn_winner.gv")
visualize.draw_net(winner, view=True, filename="nn_winner-enabled.gv", show_disabled=False)
visualize.draw_net(winner, view=True, filename="nn_winner-enabled-pruned.gv", show_disabled=False, prune_unused=True)
