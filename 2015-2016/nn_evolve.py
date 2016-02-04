# Where the magic happens

# A thought - train the first N generations with a simpler fitness function, like just trying to hit the ball
# May or may not be necessary

import os
import pickle

from neat import nn, parallel, population, visualize
from neat.config import Config
from PongAIvAI import play_training_game

games_per_net = 5
num_generations = 30

def get_ai(nn):
    # Defines a move_getter function from a neural network

    def ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
        ai.turn_number += 1
        inputs = [
            # Ball position
            ball_frect.pos[0],
            ball_frect.pos[1],
            # Player position
            paddle_frect.pos[0],
            paddle_frect.pos[1],
            # Opponent position
            other_paddle_frect.pos[0],
            other_paddle_frect.pos[1]
            # Maybe - ball velocity, previous few opponent positions, turn number
        ]
        output = nn.serial_activate(inputs)[0] # Only one output value, get that
        if output < -0.1:
            return "down"
        elif output < 0.1:
            return "none"
        else:
            return "up"

    ai.turn_number = 0
    return ai

# Use the neural network phenotype to play some games, and see how fit it is
def evaluate_genome(g):
    net = nn.create_feed_forward_phenotype(g)
    ai_to_train = get_ai(net)

    fitness = 0.0

    for game in range(games_per_net):
        # Play game
        ai_to_train.turn_number = 0
        fitness += play_training_game(ai_to_train)
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
print [g.fitness for g in pop.most_fit_genomes]
winner = None
best = -10000000
for genome in pop.most_fit_genomes:
    if genome.fitness > best:
        best = genome.fitness
        winner = genome
        index = pop.most_fit_genomes.index(genome)
print 'Best genome came in generation', index

with open('nn_winner_genome', 'wb') as f:
    pickle.dump(winner, f)

# Display the winner
print(winner)

# Get all of the best genomes
#for i in range(len(pop.most_fit_genomes)):
#    with open('nn_winner_genome_' + str(i), 'wb') as f:
#        pickle.dump(pop.most_fit_genomes[i], f)

# Plot the evolution of the best/average fitness.
visualize.plot_stats(pop, ylog=True, filename="nn_fitness.svg")
# Visualizes speciation
visualize.plot_species(pop, filename="nn_speciation.svg")
# Visualize the best network.
visualize.draw_net(winner, view=True, filename="nn_winner.gv")
visualize.draw_net(winner, view=True, filename="nn_winner-enabled.gv", show_disabled=False)
visualize.draw_net(winner, view=True, filename="nn_winner-enabled-pruned.gv", show_disabled=False, prune_unused=True)
