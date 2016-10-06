# vision red, vision green, vision blue, pain, energy, hp, birth cooldown, touch ("bump"), vision distance, constant, mem1, mem2
#inputs = [ "red", "green", "blue", "pain", "e", "hp", "norep", "touch", "vdist", "const", "mem1", "mem2" ]
#outputs= [ "speed", "turn", "bodyr", "bodyg", "bodyb", "v.eat", "m.eat", "fight", "birth", "ldist", "mem1", "mem2" ]
inputs = [ "speed", "turn", "v.red", "v.grn", "v.blu", "pain", "e", "hp", "norep", "touch", "vdist", "age", "const", "mem", "mem2" ]
outputs= [ "speed", "turn", "bodyr", "bodyg", "bodyb", "v.eat", "m.eat", "fight", "birth", "ldist", "langle", "mem", "mem2" ]
param_names = ["meat%", "bool_mutate_rate", "param_mutate_rate", "coeff_mutate_rate", "sex_birth_threshold", "asex_birth_threshold"]

import random
import constants
import math
from multiprocessing import Process, Queue
from organism import Organism, sigmoid

bool_threshold = 0.6
bool_mutate_rate = 0.05

class Creature (Organism):
    in_scales = []
    in_active = []
    intermediate = []
    out_active = []
    out_scales = []

    # State data
    accel = 0
    turn = 0
    color = (0, 0, 0)
    eat = 0
    meateat = 0
    fight = 0
    mem = 0
    mem2 = 0
    birth = 0
    lookdist = 1
    lookangle = 0

    # World-property data (position, etc)
    realdir = 0
    hp = 1.0
    id = 0
    name = "Dan"
    deathTimer = 0
    killed = False
    pain = 0
    bump = 0
    birth_cooldown = 50
    incolor = (0, 0, 0)
    real_look_pos = (0, 0) # cosmetic -- what are they actually seeing?

    def __init__(self, id, x, y, parent1=None, parent2=None, dir=5, born=None):
        self.params = {}
        self.param_names = param_names
        self.num_intermediate = 8
        self.do_intermediate = True
        Organism.__init__(self, inputs, outputs, parent1, parent2)
        self.intermediate = [0 for i in range(0, self.num_intermediate)]
        if parent1 is None:
            self.params['meat%'] = random.uniform(-1.5, 1.5)
            self.params['sex_birth_threshold'] = constants.SEX_THRESHOLD + random.uniform(-0.02, 0.02)
            self.params['asex_birth_threshold'] = constants.ASEX_THRESHOLD + random.uniform(-0.02, 0.02)
            self.realname = (chr(random.randint(0,25)+97) + chr(random.randint(0,25)+97) + random.choice(['a','e','i','o','u','y']) + chr(random.randint(0,25)+97)).title()
            self.parent1name = "<none>"
            self.parent2name = ""
            self.parents = []
            self.chromosome = "".join([chr(random.randint(0,25)+65) for i in range(104)])
            #self.energy = 1.0
        elif parent2 is None:
            self.realname = parent1.realname
            if random.random() < 0.25 and len(self.realname) > 5:
                # delete letter
                del_index = random.randint(0, len(self.realname)-1)
                self.realname = self.realname[:del_index] + self.realname[del_index+1:]
            elif random.random() > 0.75 and len(self.realname) < 10:
                # add letter
                ins_index = random.randint(0, len(self.realname))
                char = random.choice([random.choice(list('asinoer')), chr(random.randint(0,25)+97)])
                self.realname = self.realname[:ins_index] + char + self.realname[ins_index:]
            else:
                # change letter
                chg_index = random.randint(0, len(self.realname)-1)
                char = random.choice([random.choice(list('asinoer')), chr(random.randint(0,25)+97)])
                self.realname = self.realname[:chg_index] + char + self.realname[chg_index+1:]

            self.chromosome = parent1.chromosome
            mutate_index = random.randint(0, len(self.chromosome)-1)
            self.chromosome = self.chromosome[:mutate_index] + chr(random.randint(0, 25) + 65) + self.chromosome[(mutate_index+1):]
            self.realname = self.realname.title()
            #self.realname = (parent1.name + random.choice(['a','e','i','o','u','y']) + chr(random.randint(0,25)+97)).title()
            self.parent1name = parent1.name
            self.parent2name = ""
            self.parents = [ parent1.hist_entry ]
            self.ancestors = parent1.ancestors[:]
            #self.energy = parent1.energy
        else:
            self.realname = "".join([(random.choice([l1, l2]) if l1 else l2) if l2 else chr(random.randint(0,25)+97) for (l1, l2) in zip(list(parent1.realname), list(parent2.realname))]).title()
            self.chromosome = "".join([(random.choice([l1, l2]) if l1 else l2) if l2 else chr(random.randint(0,25)+97) for (l1, l2) in zip(list(parent1.chromosome), list(parent2.chromosome))])
            self.parent1name = parent1.name
            self.parent2name = parent2.name
            self.parents = [ parent1.hist_entry, parent2.hist_entry ]
            #self.energy = (parent1.energy + parent2.energy) / 2

        self.energy = constants.SEX_COST / 2

        self.is_plant = False

        #if len(self.realname) < 15:
        #    self.realname = self.realname
        #else:
        #    chromostep = (len(self.realname)-12) // 7
        #    if chromostep % 2 == 0:
        #        chromostep += 1
        #    self.realname = self.realname[0:6].title() + "-" + self.realname[6:-6:chromostep].title() + "-" + self.realname[-6:].title()

        if parent1 is not None and self.realname == parent1.name or parent2 is not None and self.realname == parent2.name:
            if parent1.name[-2:] == "IV":
                self.name = self.realname
            elif parent1.name[-3:] == "III":
                self.name = self.realname + " IV"
            elif parent1.name[-3:] == "Jr.":
                self.name = self.realname + " III"
            else:
                self.name = self.realname + " Jr."
        else:
            self.name = self.realname

        self.tile_x = x
        self.tile_y = y
        self.x = x
        self.y = y
        self.id = id
        self.alive = True
        self.age = 0
        #self.realdir = dir
        #while self.realdir == dir:
            # don't have it face the same way as its parent - so it doesn't accidentally murder them
        #    self.realdir = self.dir = random.randint(0, 3)
        self.realdir = random.uniform(0, 2*math.pi)
        self.lastdir = self.realdir
        #self.birth_cooldown = 100    # no giving birth within first 50 turns of being alive
        self.birth_cooldown = 50
        self.incolor = (1, 1, 1)
        self.color = (1, 1, 1)
        self.indist = 0
        #print("new creature: #%d" % self.id)
        self.children = []
        self.pos = (self.x, self.y)

        self.hist_entry = HistoryEntry(self, born)

        if parent2 is None:
            if parent1 is None:
                self.ancestors = [ self.hist_entry ]
            else:
                self.ancestors = parent1.ancestors[:]
        else:
            self.ancestors = parent1.ancestors[:]
            for a in parent2.ancestors:
                if a not in self.ancestors:
                    self.ancestors.append(a)

        if parent1 is not None:
            parent1.add_child(self.hist_entry)

        if parent2 is not None:
            parent2.add_child(self.hist_entry)

    def post_update(self, input_data):
        self.outs[9] = sigmoid(self.outs[9]) * constants.MAX_LOOK_DISTANCE
        self.incolor = (input_data[2], input_data[3], input_data[4])
        self.indist = input_data[13]
        self.pos = (self.x, self.y)

    def do(self, data):
        self.accel = data[0]
        self.turn = data[1]
        self.color = (data[2], data[3], data[4])
        self.eat = data[5]
        self.meateat = data[6]
        self.fight = data[7]
        self.birth = data[8]
        self.lookdist = data[9]
        self.lookangle = data[10]
        self.mem = data[11]
        self.mem2 = data[12]

    def ahead_pos(self):
        return self.ahead_pos_dist(1)
    def ahead_pos_dist(self, dist):
        #return self.calculate_pos_dir(self.dir, 1)
        return (self.x + math.cos(self.realdir) * dist, self.y + math.sin(self.realdir) * dist)
    def behind_pos(self):
        #return self.calculate_pos_dir((self.dir+2)%4, 1)
        return (self.x - math.cos(self.realdir), self.y - math.sin(self.realdir))
    #def look_pos(self):
    #    return self.calculate_pos_dir(self.dir, sigmoid(self.lookdist) * constants.MAX_LOOK_DISTANCE) # 0 ~ 3 tiles ahead

    def direction_vector(self):
        if self.dir % 2 == 0:
            if self.dir // 2 == 0:
                return (0, -1)
            else:
                return (0, 1)
        else:
            if self.dir // 2 == 0:
                return (1, 0)
            else:
                return (-1, 0)

    def calculate_pos_dir(self, dir, lookdist):
        dist = round(lookdist)
        if dir % 2 == 0:
            if dir // 2 == 0:
                return (self.tile_x, self.tile_y - dist)
            else:
                return (self.tile_x, self.tile_y + dist)
        else:
            if dir // 2 == 0:
                return (self.tile_x + dist, self.tile_y)
            else:
                return (self.tile_x - dist, self.tile_y)

    def add_child(self, entry):
        self.children.append(entry)
        self.hist_entry.add_child(entry)

    def __str__(self):
        return self.name

class HistoryEntry:
    def __init__(self, creature, born):
        self.name = creature.name
        self.parents = creature.parents[:]
        self.children = []
        self.born = born
        self.died = None
        self.descendant_proc = None
        self.descendant_queue = None
        self.descendant_started = False
        self.descendant_last_calc = (0, 0, 0, 0)

    def add_child(self, entry):
        self.children.append(entry)

    def compute_descendants(self, recount=False):
        if not self.descendant_proc:
            if not self.descendant_started or recount:
                if self.descendant_proc:
                    # if somehow recounting before being finished, kill previous attempt
                    self.descendant_proc.join()
                if not self.descendant_queue:
                    self.descendant_queue = Queue()
                self.descendant_proc = Process(target=self.fork_compute_descendants, args=(self.descendant_queue,))
                self.descendant_proc.start()
                self.descendant_last_calc = (0, 0, 0, 0)
                self.descendant_started = True
        else:
            if not self.descendant_queue.empty():
                self.descendant_last_calc = self.descendant_queue.get()
        if self.descendant_last_calc[0] == 1:
            if self.descendant_proc:
                self.descendant_proc.join()
                self.descendant_proc = None
        return self.descendant_last_calc

    def fork_compute_descendants(self, queue):
        queue.put((0, 0, 0, 0))
        total = 0
        living = 0
        generation = 0

        currlook = [] # we're doin' this iteratively so we don't exceed stack depth... oh boy
        nextlook = [ self ]
        already_seen = {}

        while len(nextlook) > 0:
            currlook = nextlook
            nextlook = []
            for i in currlook:
                nextlook += i.children
            ones = [s for s in currlook if s not in already_seen]
            total += len(ones)
            living += len([s for s in ones if not s.died])
            # this doesn't work
            #already_seen = [s for s in already_seen if not(s.died and s.died < earliest_born)]  # if died before everyone in this generation, don't need to deal with it

            # don't double-count creatures who descended from multiple people in the same family tree
            #already_seen += currlook
            for i in currlook:
                already_seen[i] = 1

            generation += 1 # max. generation depth under this creature

            # actually this isn't too bad... except the multiprocessing bit
            queue.put((0, max(0, total-1), max(0, living-1), max(0, generation-1))) # subtract ourselves from it

        total = total - 1   # don't count self
        if not self.died:
            living = living - 1 # don't count self if living
        generation = generation - 1

        queue.put((1, total, living, generation))
        return

    def die(self, time):
        self.died = time
