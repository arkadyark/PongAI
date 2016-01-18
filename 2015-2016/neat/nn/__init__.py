import math


def sigmoid_activation(bias, response, x):
    z = bias + x * response
    z = max(-60.0, min(60.0, z))
    return 1.0 / (1.0 + math.exp(-z))


def tanh_activation(bias, response, x):
    z = bias + x * response
    z = max(-60.0, min(60.0, z))
    return math.tanh(z)


def sin_activation(bias, response, x):
    z = bias + x * response
    z = max(-60.0, min(60.0, z))
    return math.sin(z)


def gauss_activation(bias, response, x):
    z = bias + x * response
    z = max(-60.0, min(60.0, z))
    return math.exp(-0.5 * z**2) / math.sqrt(2 * math.pi)


def relu_activation(bias, response, x):
    z = bias + x * response
    return z if z > 0.0 else 0


def identity_activation(bias, response, x):
    return bias + x * response


def clamped_activation(bias, response, x):
    z = bias + x * response
    return max(-1.0, min(1.0, z))


def inv_activation(bias, response, x):
    z = bias + x * response
    if z == 0:
        return 0.0

    return 1.0 / z


def log_activation(bias, response, x):
    z = bias + x * response
    z = max(1e-7, z)
    return math.log(z)


def exp_activation(bias, response, x):
    z = bias + x * response
    z = max(-60.0, min(60.0, z))
    return math.exp(z)


def abs_activation(bias, response, x):
    z = bias + x * response
    return abs(z)


def hat_activation(bias, response, x):
    z = bias + x * response
    return max(0.0, 1 - abs(z))


def square_activation(bias, response, x):
    z = bias + x * response
    return z ** 2


def cube_activation(bias, response, x):
    z = bias + x * response
    return z ** 3


activations = {'sigmoid':sigmoid_activation,
               'tanh': tanh_activation,
               'sin': sin_activation,
               'gauss': gauss_activation,
               'relu': relu_activation,
               'identity': identity_activation,
               'clamped': clamped_activation,
               'inv': inv_activation,
               'log': log_activation,
               'exp': exp_activation,
               'abs': abs_activation,
               'hat': hat_activation,
               'square': square_activation,
               'cube': cube_activation}


def find_feed_forward_layers(inputs, connections):
    '''
    Collect the layers whose members can be evaluated in parallel in a feed-forward network.
    :param inputs: list of the network input nodes
    :param connections: list of (input, output) connections in the network.

    Returns a list of layers, with each layer consisting of a set of node identifiers.
    '''

    # TODO: Detect and omit nodes whose output is ultimately never used.

    layers = []
    S = set(inputs)
    while 1:
        # Find candidate nodes C for the next layer.  These nodes should connect
        # a node in S to a node not in S.
        C = set(b for (a, b) in connections if a in S and b not in S)
        # Keep only the nodes whose entire input set is contained in S.
        T = set()
        for n in C:
            if all(a in S for (a, b) in connections if b == n):
                T.add(n)

        if not T:
            break

        layers.append(T)
        S = S.union(T)

    return layers


class FeedForwardNetwork(object):
    def __init__(self, max_node, inputs, outputs, node_evals):
        self.node_evals = node_evals
        self.input_nodes = inputs
        self.output_nodes = outputs
        self.values = [0.0] * (1 + max_node)

    def serial_activate(self, inputs):
        for i, v in zip(self.input_nodes, inputs):
            self.values[i] = v

        for node, func, bias, response, links in self.node_evals:
            s = 0.0
            for i, w in links:
                s += self.values[i] * w
            self.values[node] = func(bias, response, s)

        return [self.values[i] for i in self.output_nodes]


def create_feed_forward_phenotype(genome):
    """ Receives a genome and returns its phenotype (a neural network). """

    # Gather inputs and expressed connections.
    input_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'INPUT']
    output_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'OUTPUT']
    connections = [(cg.in_node_id, cg.out_node_id) for cg in genome.conn_genes.values() if cg.enabled]

    layers = find_feed_forward_layers(input_nodes, connections)
    node_evals = []
    used_nodes = set(input_nodes + output_nodes)
    for layer in layers:
        for node in layer:
            inputs = []
            # TODO: This could be more efficient.
            for cg in genome.conn_genes.values():
                if cg.out_node_id == node and cg.enabled:
                    inputs.append((cg.in_node_id, cg.weight))
                    used_nodes.add(cg.in_node_id)

            used_nodes.add(node)
            ng = genome.node_genes[node]
            activation_function = activations[ng.activation_type]
            node_evals.append((node, activation_function, ng.bias, ng.response, inputs))

    return FeedForwardNetwork(max(used_nodes), input_nodes, output_nodes, node_evals)


class RecurrentNetwork(object):
    def __init__(self, max_node, inputs, outputs, node_evals):
        self.max_node = max_node
        self.node_evals = node_evals
        self.input_nodes = inputs
        self.output_nodes = outputs
        self.reset()

    def reset(self):
        self.values = [[0.0] * (1 + self.max_node),
                       [0.0] * (1 + self.max_node)]
        self.active = 0

    def activate(self, inputs):
        ivalues = self.values[self.active]
        ovalues = self.values[1 - self.active]
        self.active = 1 - self.active

        for i, v in zip(self.input_nodes, inputs):
            ivalues[i] = v
            ovalues[i] = v

        for node, func, bias, response, links in self.node_evals:
            s = 0.0
            for i, w in links:
                s += ivalues[i] * w
            ovalues[node] = func(bias, response, s)

        return [ovalues[i] for i in self.output_nodes]


def create_recurrent_phenotype(genome):
    """ Receives a genome and returns its phenotype (a recurrent neural network). """

    # Gather inputs and expressed connections.
    input_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'INPUT']
    output_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'OUTPUT']

    node_inputs = {}
    used_nodes = set(input_nodes + output_nodes)
    for cg in genome.conn_genes.values():
        if not cg.enabled:
            continue

        used_nodes.add(cg.out_node_id)
        used_nodes.add(cg.in_node_id)

        if cg.out_node_id not in node_inputs:
            node_inputs[cg.out_node_id] = [(cg.in_node_id, cg.weight)]
        else:
            node_inputs[cg.out_node_id].append((cg.in_node_id, cg.weight))

    node_evals = []
    for onode, inputs in node_inputs.items():
        ng = genome.node_genes[onode]
        activation_function = activations[ng.activation_type]
        node_evals.append((onode, activation_function, ng.bias, ng.response, inputs))

    return RecurrentNetwork(max(used_nodes), input_nodes, output_nodes, node_evals)
