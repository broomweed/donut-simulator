bool_threshold = 0.7

import random
import math

class Organism:
    pos = (0, 0)
    tile_pos = (0, 0)
    color = (1, 1, 1)
    alive = True
    extant = True
    age = 0
    generation = 0
    ins = []
    outs = []
    intermediate = []
    inputs = []
    outputs = []

    def __init__(self, inputs, outputs, parent1=None, parent2=None):
        self.num_inputs = len(inputs)
        self.num_outputs = len(outputs)
        if parent1 is None:
            self.generation = 0
            self.params['bool_mutate_rate'] = 0.02 + random.uniform(-0.01, 0.01)
            self.params['param_mutate_rate'] = random.uniform(0.01, 0.03)
            self.params['coeff_mutate_rate'] = random.uniform(0.02, 0.04)
            if self.do_intermediate:
                self.in_scales = [[random.uniform(-1.0, 1.0) for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)]
                self.in_active = [[(random.random() > bool_threshold) for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)] # random booleans so not everything factors in
                self.out_active = [[(random.random() > bool_threshold) for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)]
                self.out_scales = [[random.uniform(-1.0, 1.0) for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)]
            else:
                self.out_active = [[(random.random() > bool_threshold) for j in range(0, self.num_inputs)] for i in range(0, self.num_outputs)]
                self.out_scales = [[random.uniform(-1.0, 1.0) for j in range(0, self.num_inputs)] for i in range(0, self.num_outputs)]
        elif parent2 is None:
            self.generation = parent1.generation + 1
            for i in self.param_names:
                alter = 1 + random.uniform(-parent1.params['param_mutate_rate'], parent1.params['param_mutate_rate'])
                self.params[i] = parent1.params[i] * alter
            if self.do_intermediate:
                self.in_scales = [[parent1.in_scales[i][j] + random.uniform(-self.params['coeff_mutate_rate'], self.params['coeff_mutate_rate']) for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)]
                self.in_active = [[parent1.in_active[i][j] if random.random() < self.params['bool_mutate_rate'] else not parent1.in_active[i][j]\
                                for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)] # mutate 1 in 20 times
                self.out_active = [[parent1.out_active[i][j] if random.random() < self.params['bool_mutate_rate'] else not parent1.out_active[i][j]\
                                for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)] # mutate 1 out 20 times
                self.out_scales = [[parent1.out_scales[i][j] + random.uniform(-self.params['coeff_mutate_rate'], self.params['coeff_mutate_rate']) for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)]
            else:
                self.out_active = [[parent1.out_active[i][j] if random.random() < self.params['bool_mutate_rate'] else not parent1.out_active[i][j]\
                                for j in range(0, self.num_inputs)] for i in range(0, self.num_outputs)] # mutate 1 out 20 times
                self.out_scales = [[parent1.out_scales[i][j] + random.uniform(-self.params['coeff_mutate_rate'], self.params['coeff_mutate_rate']) for j in range(0, self.num_inputs)] for i in range(0, self.num_outputs)]
        else:
            self.generation = max(parent1.generation, parent2.generation) + 1
            for i in self.param_names:
                alter = 1 + random.uniform(-parent1.params['param_mutate_rate'], parent1.params['param_mutate_rate'])
                self.params[i] = (parent1.params[i] if random.random() > 0.5 else parent2.params[i]) * alter
            self.in_scales = [[(parent1.in_scales[i][j] if random.random() > 0.5 else parent2.in_scales[i][j])\
                             + random.uniform(-self.params['coeff_mutate_rate'], self.params['coeff_mutate_rate']) for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)]
            self.in_active = [[bool(((int(parent1.in_active[i][j] if random.random() > 0.5 else parent2.in_active[i][j])-0.5) *\
                            (-1 if random.random() < self.params['bool_mutate_rate'] else 1) + 0.5))\
                            for j in range(0, self.num_inputs)] for i in range(0, self.num_intermediate)] # mutate 1 in 20 times
            self.out_active = [[bool(((int(parent1.out_active[i][j] if random.random() > 0.5 else parent2.out_active[i][j])-0.5) *\
                            (-1 if random.random() < self.params['bool_mutate_rate'] else 1) + 0.5))\
                            for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)] # mutate 1 out 20 times
            self.out_scales = [[(parent1.out_scales[i][j] if random.random() > 0.5 else parent2.out_scales[i][j])\
                             + random.uniform(-self.params['coeff_mutate_rate'], self.params['coeff_mutate_rate']) for j in range(0, self.num_intermediate)] for i in range(0, self.num_outputs)]

    #@profile
    def update(self, *input_data):
        if self.alive:
            self.ins = input_data
            if self.do_intermediate:
                self.intermediate = [(sigmoid(sum([scale * val for (scale, val) in zip(self.in_scales[i], input_data)])) if self.in_active[i] else 0) for i in range(len(self.in_scales))]
            else:
                self.intermediate = input_data
            data = [(sum([scale * val for (scale, val) in zip(self.out_scales[i], self.intermediate)]) if self.out_active[i] else 0) for i in range(len(self.out_scales))]
            self.do(data)
            self.outs = data

            self.post_update(input_data)

            self.age += 1
            #self.tile_pos = (round(self.pos[0]), round(self.pos[1]))

def sigmoid(x):
    try:
        return (math.exp(-x) + 1) ** -1
    except OverflowError:
        # sometimes if they're really emotional, they
        # can break this function
        if x < 0:
            return 0
        else:
            return 1

