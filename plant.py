inputs = [ "altitude", "energy", "e_change", "age", "seeds" ]
outputs = [ "seed", "release", "colorr", "colorg", "colorb" ]
param_names = [ "bool_mutate_rate", "param_mutate_rate", "coeff_mutate_rate", "dist_radius" ]

import random
from organism import Organism, sigmoid

class Plant (Organism):
    def __init__(self, x, y, parent=None):
        self.param_names = param_names
        self.params = {}
        self.num_intermediate = 4
        self.do_intermediate = False
        Organism.__init__(self, inputs, outputs, parent, None)
        if parent is None:
            self.color = (random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
            self.seed_dist = random.uniform(4, 12)
            self.energy = 1
            self.params['dist_radius'] = random.uniform (4, 8)
            self.species = ""
            for i in range(random.randint(1, 3)):
                self.species += gen_syl()
        else:
            self.color = (parent.color[0] + random.uniform(-0.05, 0.05), parent.color[1] + random.uniform(-0.05, 0.05), parent.color[2] + random.uniform(-0.05, 0.05))
            self.seed_dist = max(1, parent.seed_dist + random.uniform(-0.02, 0.02))
            self.energy = parent.energy / 2
            parent.energy = parent.energy / 2
            self.species = parent.species
        self.age = 0
        self.alive = True
        self.is_plant = True
        self.pos = (x, y)
        #self.tile_pos = (round(x), round(y))

    #@profile
    def update(self, *input_data):
        energy_change = input_data[2]
        Organism.update(self, *input_data)
        if self.energy == 0:
            self.alive = False
        if self.alive:
            self.energy += energy_change # PHOTO-SYNTHESIS! (but no aquatic plants)
            self.age += 1

    def post_update(self, input_data):
        pass

    def do(self, data):
        self.seed = data[0]
        self.release = data[1]
        self.color = (sigmoid(data[2]) * 2 - 1, sigmoid(data[3]) * 2 - 1, sigmoid(data[4]) * 2 - 1)

def gen_syl():
    syl = "A"
    while len(syl) < 2: # don't return 1-letter syllable
        syl = str((random.choice(list("bcdfghjklmnprstvwyz")) if random.random() > 0.3 else "") +
                   random.choice(list("aeiou")) +
                  (random.choice(list("slrn")) if random.random() > 0.7 else "") +
                  (random.choice(list("dgjklmnprstz")) if random.random() > 0.7 else ""))
    return syl
