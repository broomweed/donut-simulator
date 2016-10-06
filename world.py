# this code is awful please don't look at it
import random
import pygame
import time
import creature
from creature import Creature
from plant import Plant
from organism import sigmoid
from noise import pnoise3, snoise3
from math import log2, sin, cos, pi
from constants import *

num_creatures = 40
population = -1

world_w = 100
world_h = 100
draw_scale = 10
time = 0
spawn_timer = 0
plant_spawn_timer = 0

panel_width = 420
panel_margin = 15
panel_vmargin = 5
lineheight = 0
charwidth = 0

next_creature_id = 0
creature_positions = {}

plants = []
plant_positions = {}
plant_population = 0

selected_creature = None

fast_forward = False

# text
bigfont = None
smallfont = None

bsel_line = None
tsel_line = None
click_callback = None
click_callback_arg = 0
top_creatures_line = 4  # line to subtract from menu
brain_sel_int = False
brain_sel_out = False
brain_sel_inp = False
top_creatures = []
pop_history = []

history_mode = False
current_history_entry = None
new_history_entry = False   # ie did we just switch to it?

current_page = None

do_log = False
do_window_log = False
do_print_log = True
log_msgs = []

def init_plants():
    plant_population = 0
    create_plants(5)

def init_creatures():
    global population, next_creature_id, creature_positions
    #population = num_creatures
    #next_creature_id = num_creatures # next id for creature to be born
    #creatures = [Creature(i, random.randint(0, world_w), random.randint(0, world_h)) for i in range(0, num_creatures)]
    #for c in creatures:
    #    creature_positions[(c.tile_x, c.tile_y)] = c
    population = 0
    next_creature_id = 0
    creature_positions = {}
    creatures = []
    return creatures

def init_world():
    altitude = []
    grass = []
    alt_seed = random.uniform(0.0, 1024.0)
    grass_seed = random.uniform(0.0, 1024.0)
    for y in range(world_h):
        altitude.append([])
        for x in range(world_w):
            s = pnoise3(x/world_w * 2, y/world_h * 2, alt_seed, octaves=5, persistence=0.7, lacunarity=2.0, repeatx=2, repeaty=2, repeatz=1024)
            altitude[y].append(s)
    for y in range(world_h):
        grass.append([])
        for x in range(world_w):
            #s = max(0, (pnoise3(x/world_w * 2, y/world_h * 2, grass_seed, octaves=7, persistence=0.9, lacunarity=3.4, repeatx=2, repeaty=2, repeatz=1024) + 0.5) * 2.0 - 1.0)
            s = 0
            grass[y].append(s)

    #return [[(0 if random.random() > land_amount else random.uniform(0.1, 1.0)) for x in range(world_w)] for y in range(world_h)]
    return altitude, grass

def get_creature(point):
    if get_creatures(point) == None or len(get_creatures(point)) == 0:
        return None
    else:
        return get_creatures(point)[0]

def get_creatures(point):
    c = creature_positions.get((point[0] % world_w, point[1] % world_h))
    return c 

def get_plants(point):
    c = plant_positions.get((point[0] % world_w, point[1] % world_h))
    return c 

#@profile
def update(creatures, altitude, world, worldstate):
    global population, next_creature_id, creature_positions, time, spawn_timer, plants, plant_spawn_timer
    for creature in creatures:
        if (creature.tile_x, creature.tile_y) in creature_positions:
            creature_positions[(creature.tile_x, creature.tile_y)] = [c for c in creature_positions[(creature.tile_x, creature.tile_y)] if c != creature]
        else:
            creature_positions[(creature.tile_x, creature.tile_y)] = []

        if not creature.alive:
            creature.deathTimer += 1
            if creature.deathTimer > MAX_CORPSE_AGE:
                creature.extant = False
            elif creature.extant:
                # put it back if it's still a corpse
                creature_positions[(creature.tile_x, creature.tile_y)].append(creature)
                creature.energy = max(0, creature.energy)
                # skip its AI if it's dead
                continue

        v_angle_correction = sigmoid(creature.lookangle) * pi/4
        d = 0
        while d < sigmoid(creature.lookdist) * MAX_LOOK_DISTANCE:
            d += 0.1
            #pos = (round(creature.tile_x + cos(creature.realdir + v_angle_correction) * i), round(creature.tile_y + sin(creature.realdir + v_angle_correction) * i))
            #look_pos = (round(pos[0] % world_w), round(pos[1] % world_h))
            #neighbors = (get_creatures((look_pos)) or []) + (get_plants((look_pos)) or [])
            #if len(neighbors) > 1: # not including self
                #creature.real_look_pos = look_pos
                #vdist = i
                #icolor = neighbor.color
                #break
            target = point_in_creature((creature.x + cos(creature.realdir + v_angle_correction) * d, creature.y + sin(creature.realdir + v_angle_correction) * d))
            if target is not None:
                vdist = d
                pos = (creature.x + cos(creature.realdir) * d, creature.y + sin(creature.realdir) * d)
                creature.real_look_pos = pos
                icolor = target.color
                break
        else:
            #creature.real_look_pos = (round(creature.look_pos()[0] % world_w), round(creature.look_pos()[1] % world_h))
            vdist = round(sigmoid(creature.lookdist) * MAX_LOOK_DISTANCE)
            #icolor = (0, worldstate[creature.real_look_pos[1]][creature.real_look_pos[0]], 0)
            look_pos = (creature.x + cos(creature.realdir) * vdist, creature.y + sin(creature.realdir) * vdist)
            tile_pos = (round(creature.tile_x + cos(creature.realdir + v_angle_correction) * vdist), round(creature.tile_y + sin(creature.realdir + v_angle_correction) * vdist))
            creature.real_look_pos = look_pos
            #icolor = calculate_tile_color(creature.real_look_pos[0], creature.real_look_pos[1])
            icolor = calculate_tile_color(tile_pos[0] % world_w, tile_pos[1] % world_h)

        turn = (creature.realdir - creature.lastdir) * TURN_SPEED
        if turn > pi/2 * TURN_SPEED:
            turn = (creature.realdir - (creature.lastdir + 2*pi)) * TURN_SPEED
        elif turn < -pi/2 * TURN_SPEED:
            turn = ((creature.realdir + 2*pi) - creature.lastdir) * TURN_SPEED
            
        creature.lastdir = creature.realdir

        creature.update(creature.accel, turn, icolor[0], icolor[1], icolor[2],
                #creature.color[0], creature.color[1], creature.color[2],
                creature.pain, creature.energy, creature.hp, creature.birth_cooldown, creature.bump,
                #vdist, 1.0, creature.mem, creature.mem2)
                vdist, creature.age / 100, 1.0, creature.mem, creature.mem2)

        #for i in range(round(sigmoid(creature.lookdist) * MAX_LOOK_DISTANCE)):
        #    pos = creature.calculate_pos_dir(creature.dir, i)
        #    look_pos = (round(pos[0] % world_w), round(pos[1] % world_h))
        #    neighbor = get_creature(look_pos)
        #    if neighbor is not None:
        #        creature.real_look_pos = look_pos
        #        break
        #else:
        #    creature.real_look_pos = (round(creature.look_pos()[0] % world_w), round(creature.look_pos()[1] % world_h))
            
        creature.pain = 0 # to be added to in next frame
        creature.bump = 0 # whether or not they're being restricted in movement b/c someone's there

        if creature.hp < 1:
            creature.hp += sigmoid(creature.energy - MIN_CREATURE_ENERGY - HP_HALF_E_LEVEL) * 0.2 # recover HP
        creature.hp = max(0, min(1, creature.hp))

        turnamt = sigmoid(creature.turn/8) * 2 - 1
        creature.realdir += turnamt
        #while creature.realdir < 0:
        #    creature.realdir += 4
        creature.energy -= TURN_COST * turnamt
        creature.turn = 0

        #creature.dir = int(round(creature.realdir) % 4)

        creature.age += 1

        # dir:
        # 0 = up
        # 1 = right
        # 2 = down
        # 3 = left

        #neighbor = get_creature(creature.ahead_pos())
        #bneighbor = get_creature(creature.behind_pos())

        creature.tile_x = int(round(creature.x) % world_w)
        creature.tile_y = int(round(creature.y) % world_h)

        neighbors = []
        for x in range(creature.tile_x-1, creature.tile_x+2):
            for y in range(creature.tile_y-1, creature.tile_y+2):
                if get_creatures((x, y)) is not None:
                    neighbors += get_creatures((x, y))
                if get_plants((x, y)) is not None:
                    neighbors += get_plants((x, y))

        dirvec = (cos(creature.realdir), sin(creature.realdir))
        accel = sigmoid(creature.accel) * 2 - 1
        newpos = (creature.x + dirvec[0] * accel * MOVE_SPEED, creature.y + dirvec[1] * accel * MOVE_SPEED)
        bumped = False

        for n in neighbors:
            newdist = (newpos[0] - n.pos[0]) ** 2 + (newpos[1] - n.pos[1]) ** 2 
            if newdist < 2:
                if newdist < (creature.x - n.pos[0]) ** 2 + (creature.y - n.pos[1]) ** 2:
                    # only prevent movement if moved closer than last time (this might not work the way I want?)
                    # but this should prevent creatures from getting stuck under babies
                    creature.bump += 1
                    if not n.is_plant:
                        n.bump += 1
                    bumped = True

        if not bumped:
            creature.x = newpos[0]
            creature.y = newpos[1]

        #if (creature.accel > 0 and neighbor is None) or (creature.accel < 0 and bneighbor is None):
            #accel = sigmoid(creature.accel) * 2 - 1 # -1 ~ 1
            #creature.energy -= MOVE_COST * abs(accel)
            ##dirvec = creature.direction_vector()
            #dirvec = (cos(creature.realdir), sin(creature.realdir))
            #creature.x += dirvec[0] * accel * 0.4
            #creature.y += dirvec[1] * accel * 0.4
        #elif creature.accel != 0:
            #creature.bump += 1
            #if neighbor is not None and creature.accel > 0:
                #neighbor.bump += 1
            #elif bneighbor is not None and creature.accel < 0:
                #bneighbor.bump += 1

        creature.x %= world_w
        creature.y %= world_h

        creature.tile_x = int(round(creature.x) % world_w)
        creature.tile_y = int(round(creature.y) % world_h)

        if altitude[creature.tile_y][creature.tile_x] > WATER_LEVEL:
            creature.energy *= (1 - BE_ALIVE_RATIO_COST)
            creature.energy -= BE_ALIVE_COST
        else:
            creature.energy *= (1 - TREAD_WATER_COST - BE_ALIVE_COST) # treading water

        ahead_pos = creature.ahead_pos()
        neighbor = get_creature(ahead_pos)

        if creature.meateat > 0:
            #log("%d: %d, %d -> %d, %d" % (creature.id, ahead_pos[0], ahead_pos[1], creature.tile_x, creature.tile_y))
            if neighbor is not None and not neighbor.is_plant and neighbor.extant and not neighbor.alive:
                creature.energy -= creature.eat * MEAT_EAT_COST    # cost: 0 ~ 1/10 carnivory
                if neighbor.energy > 0:
                    eatAmt = min(neighbor.energy, creature.eat)
                    energy_gain = eatAmt * MEAT_EAT_RATIO * (sigmoid(creature.params["meat%"]) - MEAT_POISON_CUTOFF)
                    creature.energy += energy_gain
                    neighbor.energy -= eatAmt
                    if neighbor.energy <= 0:
                        neighbor.extant = False
                        if population <= 60 and do_log:
                            log("[^^] %s ate %s! (%+.2fe)" % (creature.name, neighbor.name, energy_gain))
                            pass
                    else:
                        if population <= 40 and do_log:
                            log("[#@#@] %s is eating %s! (%+.2fe)" % (creature.name, neighbor.name, energy_gain))
                            pass

        #if creature.eat > 0:
        #        eatAmt = (sigmoid(creature.eat) - 0.5) * EAT_SPEED  # between 0 and 1: attempted amount to eat of grass
        #        creature.energy -= eatAmt * EAT_COST                # EAT_COST is cost per unit of *attempted* eating
        #        if altitude[creature.tile_y][creature.tile_x] > WATER_LEVEL:
        #            eaten = eatAmt * (worldstate[creature.tile_y][creature.tile_x]) * ((1 - sigmoid(creature.params["meat%"])) - (1 - VEG_POISON_CUTOFF))
        #            creature.energy += eaten * EAT_RATIO
        #            worldstate[creature.tile_y][creature.tile_x] -= eaten
        #            worldstate[creature.tile_y][creature.tile_x] = max(worldstate[creature.tile_y][creature.tile_x], 0)
                    # amount to eat = eat * food amt there - still takes 6 frames to eat at eat = 6
        if creature.eat > 0:
            eatAmt = (sigmoid(creature.eat) - 0.5) * EAT_SPEED  # between 0 and 1: attempted amount to eat of plant
            creature.energy -= eatAmt * EAT_COST                # EAT_COST is cost per unit of *attempted* eating
            target = point_in_creature(creature.ahead_pos_dist(1.7))
            if target and target.is_plant and target.alive and target.energy > 0:
                eaten = eatAmt * target.energy * ((1 - sigmoid(creature.params["meat%"])) - (1 - VEG_POISON_CUTOFF))
                eaten = eatAmt * target.energy * ((1 - sigmoid(creature.params["meat%"])) - (1 - VEG_POISON_CUTOFF))
                target.energy -= eaten * 25
                creature.energy += eaten * EAT_RATIO
                if target.energy < 0:
                    target.alive = False
        
        if creature.fight > 0:
            fightAmt = sigmoid(creature.fight) * 2 - 1
            if neighbor is not None and neighbor.alive:
                creature.energy -= fightAmt * FIGHT_COST # cost: 0 ~ 1/5 fight
                damage = fightAmt * FIGHT_RATIO * neighbor.hp # proportional to target's HP
                neighbor.hp -= damage
                neighbor.pain += fightAmt * 2
                neighbor.hp = max(0, neighbor.hp)
                if neighbor.hp == 0:
                    neighbor.killed = True
                    kill(neighbor, natural=False)
                    if population <= 50 and do_log:
                        log("[XX] %s killed %s!" % (creature.name, neighbor.name))
                        pass
                else:
                    if population <= 40 and do_log:
                        log("[!!] %s attacked %s for %.2f damage! (%s: %.2fh)" % (creature.name, neighbor.name, damage, neighbor.name, neighbor.hp))
                        pass

        if creature.birth_cooldown > 0:
            creature.birth_cooldown -= 1

        # sexual reproduction
        if creature.energy > SEX_REQ and creature.birth_cooldown == 0 and creature.birth > creature.params['sex_birth_threshold']:
            neighbors = []
            for x in range(-2, 3):
                for y in range(-2, 3):
                    neighbors.append(get_creature((creature.tile_x + x, creature.tile_y + y)))
            for neighbor in neighbors:
                if neighbor is not None and neighbor is not creature and neighbor.birth > neighbor.params['sex_birth_threshold'] and neighbor.energy > SEX_REQ and neighbor.birth_cooldown == 0:
                    if creature.generation < 3 or neighbor.generation < 3 or compare_chromosomes(creature.chromosome, neighbor.chromosome) <= 7:
                        # allow very new creatures to interbreed so their genes might pass on, but otherwise they have to be closely related (for speciation)
                        #if get_creature((creature.behind_pos()[0] % world_w, creature.behind_pos()[1] % world_h)) is None:
                        if not creature_overlap(creature.behind_pos()):
                            creatures.append(Creature(next_creature_id, creature.behind_pos()[0] % world_w, creature.behind_pos()[1] % world_h, creature, neighbor, born=time))
                            creature.birth_cooldown = SEX_COOLDOWN
                            neighbor.birth_cooldown = SEX_COOLDOWN
                            creature.energy -= SEX_COST
                            neighbor.energy -= SEX_COST
                            if population <= 100 and do_log:
                                log("[<3] %s and %s gave birth to %s! pop: %d" % (creature.name, neighbor.name, creatures[-1].name, population))
                                pass
                            next_creature_id += 1
                            population += 1
                    #else:
                        #if population <= 500 and do_log:
                        #log("[:(] %s and %s are incompatible" % (creature.name, neighbor.name))

        # asexual reproduction
        if creature.energy > ASEX_REQ and creature.birth_cooldown == 0 and creature.birth > creature.params['asex_birth_threshold']:
            #if get_creature(creature.behind_pos()) is None:
            if not creature_overlap(creature.behind_pos()):
                creatures.append(Creature(next_creature_id, creature.behind_pos()[0] % world_w, creature.behind_pos()[1] % world_h, creature, born=time))
                creature.birth_cooldown = ASEX_COOLDOWN
                creature.energy -= ASEX_COST
                if population <= 80 and do_log:
                    log("[++] %s gave birth to %s! pop: %d" % (creature.name, creatures[-1].name, population))
                    pass
                next_creature_id += 1
                population += 1

        if creature.energy < MIN_CREATURE_ENERGY and creature.alive:
            #log("creature #%d: %f / %f" % (creature.id, creature.energy, MIN_CREATURE_ENERGY))
            if creature.age > NOTABLE_AGE:
                if population <= 60 and do_log:
                    log("[--] %s died of starvation" % creature.name)
                    pass
            kill(creature, natural=True)

        if creature.extant:
            if (creature.tile_x, creature.tile_y) in creature_positions:
                creature_positions[(creature.tile_x, creature.tile_y)].append(creature)
            else:
                creature_positions[(creature.tile_x, creature.tile_y)] = [creature]

    for plant in plants:
        alt = altitude[plant.tile_pos[1] % world_w][plant.tile_pos[0] % world_h] 
        if alt > WATER_LEVEL:
            e_change = (2 - (world[plant.tile_pos[1] % world_w][plant.tile_pos[0] % world_h]) * 3) / 80
        else:
            e_change = -1
        plant.update(alt, plant.energy, e_change, plant.age / 100, 0)

        if plant.energy < 0:
            plant.energy = 0
            plant.alive = False
        if plant.energy > PLANT_REPRODUCTIVE_THRESHOLD and plant.release > 0:
            if plant_population < MAX_PLANTS:
                seed_angle = random.uniform(-pi, pi)
                x = (plant.pos[0] + cos(seed_angle) * plant.seed_dist) % world_w
                y = (plant.pos[1] + sin(seed_angle) * plant.seed_dist) % world_h
                #if not creature_overlap((x, y)):
                if not point_within_radius_of_creature((x, y), plant.params['dist_radius']):
                    plant_child = Plant(x, y, parent=plant)
                    register_plant(plant_child)
                else:
                    plant.energy -= PLANT_REPRODUCTIVE_THRESHOLD / 2    # crowding penalty


    if plant_population == 0:
        create_plants(5)

    #for y in range(len(worldstate)):
        #for x in range(len(worldstate[y])):
            #if altitude[y][x] > WATER_LEVEL and worldstate[y][x] < world[y][x]:
                #worldstate[y][x] += GRASS_GROW_RATE * random.uniform(0.2, 1.3) # grass grow rate

    time += 1
    spawn_timer += 1
    plant_spawn_timer += 1
    if time % 100 == 0:
        if do_log:
            log(" ~~  frame %d ~ population: %d" % (time, population))
            best_creature = max(creatures, key=lambda x: x.energy)
            log("         best creature: %s (e: %.2f; hp: %.1f%%; age: %.2f d; m%%e: %.1f%%; bt: %.2f)" %\
                    (best_creature.name, best_creature.energy, best_creature.hp * 100, float(best_creature.age)/100, sigmoid(best_creature.params['meat%']) * 100, best_creature.birth))

    if time % 10 == 0:
        pop_history.append((population, plant_population / 4))
        if len(pop_history) > panel_width + world_w * draw_scale:
            pop_history.pop(0)

    if population == 0 or spawn_timer > log2(population)/log2(6) * 40:
        num_to_spawn = population // 7 + 1
        spawn_creature(num_to_spawn)
        if do_log:
            log(" ##  %d ~ %s" % (time, ", ".join([c.name for c in creatures[-num_to_spawn:]])))
            pass
        spawn_timer = 0

    if plant_population == 0 or plant_spawn_timer > log2(plant_population)/log2(2) * 60:
        create_plants(1)
        plant_spawn_timer = 0

    #creatures = [c for c in creatures if c.extant] # no old corpses

def kill(creature, natural=True):
    # :(
    global population, next_creature_id, num_creatures
    if creature.alive:
        creature.alive = False
        creature.hist_entry.die(time)
        #if natural and creature.age < CORPSE_AGE:
        #    creature.extant = False # don't leave a corpse if not enough creatures, otherwise world fills up with corpses
            # however, leave a corpse if killed so they can eat it if necessary; also if they were old enough
        if natural:
            creature.deathTimer = MAX_CORPSE_AGE - MAX_NATURAL_CORPSE_AGE
        else:
            creature.deathTimer = 0
        population -= 1

def spawn_creature(amt):
    global next_creature_id, population
    for i in range(amt):
        x = random.uniform(0, world_w)
        y = random.uniform(0, world_h)
        while point_in_creature((x, y)):
            x = random.uniform(0, world_w)
            y = random.uniform(0, world_h)

        creatures.append(Creature(next_creature_id, x, y, born=time))
        next_creature_id += 1
        population += 1

def create_plants(amt):
    for i in range(amt):
        plant = Plant(random.uniform(0, world_w), random.uniform(0, world_h))
        plant.energy = random.uniform(0, PLANT_REPRODUCTIVE_THRESHOLD)
        register_plant(plant)

def register_plant(plant):
    global plants, plant_population
    plant.tile_pos = (round(plant.pos[0]) % world_w, round(plant.pos[1]) % world_h)
    plant_population += 1
    plants.append(plant)
    if plant.tile_pos in plant_positions:
        plant_positions[plant.tile_pos].append(plant)
    else:
        plant_positions[plant.tile_pos] = [plant]

def compare_chromosomes(c1, c2):
    # this doesn't really work with the new naming system
    diff = 0
    for i in range(len(c1)):
        if c1[i] != c2[i]:
            diff += 1
    return diff

def creature_overlap(point):
    return point_within_radius_of_creature(point, 1)

def point_in_creature(point):
    return point_within_radius_of_creature(point, 0.5)

def point_within_radius_of_creature(point, radius):
    neighbors = []
    tile_x = int(point[0])
    tile_y = int(point[1])
    for x in range(tile_x-1, tile_x+2):
        for y in range(tile_y-1, tile_y+2):
            if get_creatures((x, y)) is not None:
                neighbors += get_creatures((x, y))
            if get_plants((x, y)) is not None:
                neighbors += get_plants((x, y))

    for n in neighbors:
        newdist = (point[0] - n.pos[0]) ** 2 + (point[1] - n.pos[1]) ** 2 
        if newdist < radius ** 2:
            return n

    return None

#@profile
def draw(win, landscape, world, altitude, creatures, plants):
    global selected_creature, bsel_line, click_callback, click_callback_arg, top_creatures, new_history_entry
    win.fill((0, 0, 0))
    mouse_pos = pygame.mouse.get_pos()
    if mouse_pos[0] < world_w * draw_scale:
        highlight_tile = (mouse_pos[0] // draw_scale, mouse_pos[1] // draw_scale)
    else:
        highlight_tile = None
    win.blit(landscape, (0, 0))
    if highlight_tile:
        pygame.draw.rect(win, (0, 0, 0), ((highlight_tile[0]*draw_scale, highlight_tile[1]*draw_scale), (draw_scale, draw_scale)), 1)

    if selected_creature and not selected_creature.is_plant:
        look_pos = selected_creature.real_look_pos
        #look_pos = (round(selected_creature.x + selected_creature.indist * cos(selected_creature.realdir)), round(selected_creature.y + selected_creature.indist * sin(selected_creature.realdir)))
        pygame.draw.circle(win, (0, 255, 255), (round(look_pos[0]*draw_scale), round(look_pos[1]*draw_scale)), 4, 1)

    hover_creature = point_in_creature((mouse_pos[0] / draw_scale, mouse_pos[1] / draw_scale))

    for c in creatures:
        #if c.extant and c.age < 25:
        #    color = (min(1, max(0, 1-(c.age/25) + c.incolor[0])),
        #             min(1, max(0, 1-(c.age/25) + c.incolor[1])),
        #             min(1, max(0, 1-(c.age/25) + c.incolor[2])))
        #elif c.extant and c.age > 40 and c.birth_cooldown > 40:
        #    color = (0, 0, (c.birth_cooldown-40)/(ASEX_COOLDOWN-40))
        #elif c.extant and c.fight > 0.5:
        #    color = (c.fight, 0, 0)
        #else:
        color = c.incolor

        #if c.alive:
        #    rightcolor = (max(0, min(255, 255 * color[0])),max(0, min(255, 255 * color[1])),max(0, min(255, 255 * color[2])))
        #    pygame.draw.circle(win, rightcolor, (round(draw_scale*c.x) + draw_scale//2, round(draw_scale*c.y) + draw_scale//2), draw_scale//2 + 2)

        #rightcolor = (max(0, min(255, 128 * c.color[0] + 128)),max(0, min(255, 128 * c.color[1] + 128)),max(0, min(255, 128 * c.color[2] + 128)))
        #rightcolor = (max(0, min(255, 255 * c.color[0])),max(0, min(255, 255 * c.color[1])),max(0, min(255, 255 * c.color[2])))
        rightcolor = (255 * sigmoid(c.color[0]), 255 * sigmoid(c.color[1]), 255 * sigmoid(c.color[2]))
        #pygame.draw.circle(win, rightcolor, (draw_scale*(c.tile_x) + draw_scale//2, draw_scale*(c.tile_y) + draw_scale//2), draw_scale//2)
        pygame.draw.circle(win, rightcolor, (round(draw_scale*(c.x)), round(draw_scale*(c.y))), draw_scale//2)

        #pygame.draw.circle(win, outlinecolor, (draw_scale*(c.tile_x) + draw_scale//2, draw_scale*(c.tile_y) + draw_scale//2), draw_scale//2, 1)
        if selected_creature and c.id == selected_creature.id:
            if c.alive:
                outlinecolor = (0, 0, 255)
            else:
                outlinecolor = (255, 0, 255)
        else:
            if c.alive:
                outlinecolor = (0, 0, 0)
            else:
                outlinecolor = (255, 0, 0)

        pygame.draw.circle(win, outlinecolor, (round(draw_scale*(c.x)), round(draw_scale*(c.y))), draw_scale//2, 1)
        #if c.dir == 0:
            #eye_pos = (draw_scale * c.tile_x + draw_scale//2, draw_scale * c.tile_y + draw_scale//4)
        #    eye_pos = (draw_scale * c.x + draw_scale//2, draw_scale * c.y + draw_scale//4)
        #elif c.dir == 1:
            #eye_pos = (draw_scale * c.tile_x + 3*draw_scale//4, draw_scale * c.tile_y + draw_scale//2)
        #    eye_pos = (draw_scale * c.x + 3*draw_scale//4, draw_scale * c.y + draw_scale//2)
        #elif c.dir == 2:
            #eye_pos = (draw_scale * c.tile_x + draw_scale//2, draw_scale * c.tile_y + 3*draw_scale//4)
        #    eye_pos = (draw_scale * c.x + draw_scale//2, draw_scale * c.y + 3*draw_scale//4)
        #elif c.dir == 3:
            #eye_pos = (draw_scale * c.tile_x + draw_scale//4, draw_scale * c.tile_y + draw_scale//2)
        #    eye_pos = (draw_scale * c.x + draw_scale//4, draw_scale * c.y + draw_scale//2)
        #else:
        #    log("unknown dir %d" % c.dir)
        eye_pos = (draw_scale * c.x + cos(c.realdir) * draw_scale // 4, draw_scale * c.y + sin(c.realdir) * draw_scale // 4)

        eye_pos = (round(eye_pos[0]), round(eye_pos[1]))

        pygame.draw.circle(win, outlinecolor, eye_pos, draw_scale // 4)

    for p in plants:
        color = (sigmoid(p.color[0]) * 255, sigmoid(p.color[1]) * 255, sigmoid(p.color[2]) * 255)
        pygame.draw.circle(win, color, (round(p.pos[0]*draw_scale), round(p.pos[1]*draw_scale)), draw_scale // 2)
        #pygame.draw.circle(win, (255 * (sigmoid(p.energy/10) * 2 - 1), 255 * (sigmoid(p.energy/10) * 2 - 1), 255 * (sigmoid(p.energy/10) * 2 - 1)),
                #(round(p.pos[0]*draw_scale), round(p.pos[1]*draw_scale)), draw_scale // 2, 2)

    win.fill((0, 0, 0), ((world_w * draw_scale, 0), (panel_width, world_h * draw_scale)))


    #if highlight_tile:
        #hover_creature = get_creature(highlight_tile)
    #else:
        #hover_creature = None
    if not hover_creature and selected_creature:
        hover_creature = selected_creature
    if hover_creature and not hover_creature.is_plant and not hover_creature.extant:
        hover_creature = None

    if current_page:
        if current_page == "exit_confirm":
            labeltext = "Exit"
            infotexts = [
                    ("Are you sure you want to exit?", "", (0,0,0)),
                    ("You will lose all progress!", "", (0,0,0)),
                    ("", "", (0,0,0)),
                    (" ", "yes, exit", (128, 255, 128), real_exit, 0),
                    (" ", "no, go back", (255, 128, 128), cancel_exit, 0),
                ]
            bottom_lines = []
    else:
        if current_history_entry is not None and (hover_creature is None or hover_creature == selected_creature):
            # don't display history if actually *hovering*, but do it if something is selected
            labeltext = current_history_entry.name
            infotexts = [
                    ("lifespan ", "%.2f ~ %s" % (current_history_entry.born / 100, ("%.2f" % (current_history_entry.died / 100)) if current_history_entry.died else ""), (0, 255, 0)),
                ]
            if new_history_entry:
                descendants = current_history_entry.compute_descendants(recount=True)
                new_history_entry = False
            else:
                descendants = current_history_entry.compute_descendants() # use old one unless explicitly refreshing OR if browsing to a new entry
            if descendants[0] == 0:
                infotexts.append(("{:,}+ descendant{} ({} living)".format(descendants[1], "" if descendants[1] == 1 else "s", "??" if descendants[2] == 0 else "{:,}+".format(descendants[2])), "", (0,0,0)))
                infotexts.append(("Parent to {:,}+ generation{}".format(descendants[3], "" if descendants[3] == 1 else "s"), "", (0,0,0)))
                infotexts.append((" ", "...counting descendants...", (255, 255, 255)))
            else:
                infotexts.append(("{:,} descendant{} ({:,} living)".format(descendants[1], "" if descendants[1] == 1 else "s", descendants[2]), "", (0,0,0)))
                infotexts.append(("Parent to {:,} generation{}".format(descendants[3], "" if descendants[3] == 1 else "s"), "", (0,0,0)))
                infotexts.append((" ", "recount descendants", (255, 128, 255), recount_descendants, 0))

            infotexts.append(("", "", (0,0,0)))
            infotexts.append(("", "PARENTS", (128,255,200)))
            if len(current_history_entry.parents) > 0:
                infotexts.append((" ", current_history_entry.parents[0].name, (255, 255, 128), select_parent_1, 0))
                if len(current_history_entry.parents) > 1:
                    infotexts.append((" ", current_history_entry.parents[1].name, (255, 255, 128), select_parent_2, 0))
                else:
                    infotexts.append((" ", "<asexually spawned>", (128, 128, 128)))
            else:
                infotexts.append((" ", "<primordially created>", (128, 128, 128)))
                infotexts.append((" This creature is an ancestor.", "", (0,0,0)))

            if len(current_history_entry.children) > 0:
                infotexts.append(("", "", (0,0,0)))
                infotexts.append(("", "CHILDREN", (200, 128, 255)))
                for i in range(len(current_history_entry.children)):
                    descendants = current_history_entry.children[i].compute_descendants()
                    if descendants[0] == 0:
                        infotexts.append((" ", "%s (%d/%d%s) . . ." % (current_history_entry.children[i].name, descendants[1], descendants[2], ", living" if not current_history_entry.children[i].died else ""),
                                    (255, 255, 128), select_child, i))
                    else:
                        infotexts.append((" ", "%s (%d/%d%s)" % (current_history_entry.children[i].name, descendants[1], descendants[2], ", living" if not current_history_entry.children[i].died else ""),
                                    (255, 255, 128), select_child, i))

            bottom_lines = []
                
        elif hover_creature:
            if hover_creature.is_plant:
                labeltext = "Plant!"
                infotexts = [
                        ("generation ", "%d" % hover_creature.generation, ((1-sigmoid(hover_creature.generation/10))*255, 255, sigmoid(hover_creature.generation/25)*255)),
                        ("age ", "%.2fd" % (hover_creature.age / 100), (sigmoid(-hover_creature.age/100) * 255, sigmoid(hover_creature.age/100) * 255, 0)),
                        ("energy ", "%.2f" % hover_creature.energy,
                            (255*(1-(sigmoid(max(MIN_CREATURE_ENERGY, hover_creature.energy - MIN_CREATURE_ENERGY)) * 2 - 1)),
                            (sigmoid(max(MIN_CREATURE_ENERGY, hover_creature.energy - MIN_CREATURE_ENERGY)) * 2 - 1) * 255, 0)),
                        ("", "", (0,0,0)),
                        ("species ", hover_creature.species, (255, 128, 128)),
                    ]
                bottom_lines = []
            else:
                labeltext = hover_creature.name
                infotexts = [
                        ("", "view family tree entry", (255, 255, 128), select_creature_entry, 0),
                        ("", "", (0,0,0)),
                        ("", "STATS", (255, 128, 255)),
                        ("generation ", "%d" % hover_creature.generation, ((1-sigmoid(hover_creature.generation/10))*255, 255, sigmoid(hover_creature.generation/25)*255)),
                        ("age ", "%.2fd" % (hover_creature.age / 100), (sigmoid(-hover_creature.age/100) * 255, sigmoid(hover_creature.age/100) * 255, 0)),
                        ("energy ", "%.2f" % hover_creature.energy,
                            (255*(1-(sigmoid(max(MIN_CREATURE_ENERGY, hover_creature.energy - MIN_CREATURE_ENERGY)) * 2 - 1)),
                            (sigmoid(max(MIN_CREATURE_ENERGY, hover_creature.energy - MIN_CREATURE_ENERGY)) * 2 - 1) * 255, 0)),
                            # max necessary so it doesn't exceed 255
                        ("hp ", "%.0f%%" % (hover_creature.hp * 100), (255 * min(1, (1-hover_creature.hp)), 255 * max(0, (hover_creature.hp)), 0)),
                        ("meat efficiency ", "%.1f%%" % (sigmoid(hover_creature.params['meat%']) * 100), (255 * (sigmoid(hover_creature.params['meat%'])), 255 * (1-sigmoid(hover_creature.params['meat%'])), 100)),
                        ("birth factor ", "%+.2f" % hover_creature.birth, (max(0, 255 * (sigmoid(-hover_creature.birth * 5) * 2 - 1)), 255, max(0, 255 * (sigmoid(hover_creature.birth * 5) * 2 - 1)))),
                        ("asex threshold ", "%+.2f" % hover_creature.params['asex_birth_threshold'], ((max(0, 255 * (sigmoid(-hover_creature.params['asex_birth_threshold'] * 5) * 2 - 1)),
                            255, max(0, 255 * (sigmoid(hover_creature.params['asex_birth_threshold'] * 5) * 2 - 1))))),
                        ("sex threshold ", "%+.2f" % hover_creature.params['sex_birth_threshold'], ((max(0, 255 * (sigmoid(-hover_creature.params['sex_birth_threshold'] * 5) * 2 - 1)),
                            255, max(0, 255 * (sigmoid(hover_creature.params['sex_birth_threshold'] * 5) * 2 - 1))))),
                        #("memory ", "%.2f | %.2f" % (hover_creature.mem, hover_creature.mem2), (255, 255, 255)),
                        ("", "", (0,0,0)),
                        ("", "PARENT" if hover_creature.parent2name != "" else "PARENT", (128, 255, 255)),
                        (" ", hover_creature.parent1name, (255, 255, 128) if hover_creature.parent1name != "<none>" else (128, 128, 128), select_parent_1 if hover_creature.parent1name != "<none>" else None, 0),
                    ]
                if hover_creature.parent2name:
                    infotexts.append((" ", hover_creature.parent2name, (255, 255, 128), select_parent_2, 0))
                infotexts += [
                        ("", "", (0,0,0)),
                        #("", "HAD A BABY", (255*(1-(max(SEX_COOLDOWN, ASEX_COOLDOWN) - hover_creature.birth_cooldown)/max(SEX_COOLDOWN, ASEX_COOLDOWN) if hover_creature.age > 50 else 0),
                        #                    255*(1-(max(SEX_COOLDOWN, ASEX_COOLDOWN) - hover_creature.birth_cooldown)/max(SEX_COOLDOWN, ASEX_COOLDOWN) if hover_creature.age > 50 else 0), 0)),
                        ("", "MUTATION RATES", (128, 255, 128)),
                        ("parameters \u00b1", "%.2f%%" % (hover_creature.params['param_mutate_rate'] * 100),
                                 (255 * max(0, sigmoid(hover_creature.params['param_mutate_rate'] * 100 - 2) * 2 - 1),
                                  255, 255 * max(0, sigmoid(-hover_creature.params['param_mutate_rate'] * 100 + 2) * 2 - 1))),
                        ("coeff #s \u00b1", "%.4f" % (hover_creature.params['coeff_mutate_rate']),
                                 (255 * max(0, sigmoid(hover_creature.params['coeff_mutate_rate'] * 100 - 3) * 2 - 1),
                                  255, 255 * max(0, sigmoid(-hover_creature.params['coeff_mutate_rate'] * 100 + 3) * 2 - 1))),
                        ("coeffs on/off ", "%.2f%%" % (hover_creature.params['bool_mutate_rate'] * 100),
                                 (255 * max(0, sigmoid(hover_creature.params['bool_mutate_rate'] * 100 - 2) * 2 - 1),
                                  255, 255 * max(0, sigmoid(-hover_creature.params['bool_mutate_rate'] * 100 + 2) * 2 - 1))),
                        ("", "", (0, 0, 0)),
                        ("", "ANCESTORS" if len(hover_creature.ancestors) > 1 else "ANCESTOR", (255, 128, 128)),
                    ]

                for i in range(len(hover_creature.ancestors)):
                    infotexts.append((" ", hover_creature.ancestors[i].name, (255, 255, 128), select_ancestor, i))

                infotexts += [
                        ("", "", (0, 0, 0)),
                        ("", "CHROMOSOME", (255, 200, 128)),
                        ("a ", hover_creature.chromosome[:26], (128, 128, 128)),
                        ("b ", hover_creature.chromosome[26:52], (128, 128, 128)),
                        ("c ", hover_creature.chromosome[52:78], (128, 128, 128)),
                        ("d ", hover_creature.chromosome[78:], (128, 128, 128)),
                    ]

                labeltext = hover_creature.name
                if not hover_creature.alive:
                    infotexts.insert(0, ("", "", (0, 0, 0), 0))
                    infotexts.insert(0, ("", "DEAD", (255, 0, 0), 0))
                bottom_lines = [
                    "               == BRAIN ==",
                    "Sense Input Coef. Hidd. Coef. Output Action",
                ]
                brain_length = max(len(hover_creature.ins), len(hover_creature.intermediate), len(hover_creature.outs))
                if bsel_line and bsel_line >= brain_length:
                    bsel_line = None
                for i in range(brain_length):
                    if bsel_line is not None and (brain_sel_int or brain_sel_out or brain_sel_inp):
                        if brain_sel_int:
                            bottom_lines.append("%5s %s %s %s %s %s %s" % (
                                        creature.inputs[i] if len(creature.inputs) > i else " " * 2,
                                        ("%5.2f" % hover_creature.ins[i]) if len(hover_creature.ins) > i else " " * 5,
                                        ("%5.2f" % hover_creature.in_scales[brain_length-bsel_line-1][i])\
                                            if brain_length-bsel_line-1 < len(hover_creature.in_scales) and len(hover_creature.in_scales[brain_length-bsel_line-1]) > i \
                                            and hover_creature.in_active[brain_length-bsel_line-1][i] else " " * 5,
                                        ("%5.2f" % hover_creature.intermediate[i]) if len(hover_creature.intermediate) > i else " " * 5,
                                        ("%5.2f" % hover_creature.out_scales[i][brain_length-bsel_line-1])\
                                            if i < len(hover_creature.out_scales) and len(hover_creature.out_scales[i]) > brain_length-bsel_line-1\
                                            and hover_creature.out_active[i][brain_length-bsel_line-1] else " " * 5,
                                        ("%6.2f" % hover_creature.outs[i]) if len(hover_creature.outs) > i else " " * 6,
                                        creature.outputs[i] if len(creature.outputs) > i else ""))
                        elif brain_sel_out:
                            bottom_lines.append("%5s %s       %s %s %s %s" % (
                                        creature.inputs[i] if len(creature.inputs) > i else " " * 5,
                                        ("%5.2f" % hover_creature.ins[i]) if len(hover_creature.ins) > i else " " * 5,
                                        ("%5.2f" % hover_creature.intermediate[i]) if len(hover_creature.intermediate) > i else " " * 5,
                                        ("%5.2f" % hover_creature.out_scales[brain_length-bsel_line-1][i])\
                                            if brain_length-bsel_line-1 < len(hover_creature.out_scales) and len(hover_creature.out_scales[brain_length-bsel_line-1]) > i\
                                            and hover_creature.out_active[brain_length-bsel_line-1][i] else " " * 5,
                                        ("%6.2f" % hover_creature.outs[i]) if len(hover_creature.outs) > i else " " * 6,
                                        creature.outputs[i] if len(creature.outputs) > i else ""))
                        elif brain_sel_inp:
                            bottom_lines.append("%5s %s %s %s       %s %s" % (
                                        creature.inputs[i] if len(creature.inputs) > i else " " * 5,
                                        ("%5.2f" % hover_creature.ins[i]) if len(hover_creature.ins) > i else " " * 5,
                                        ("%5.2f" % hover_creature.in_scales[i][brain_length-bsel_line-1])\
                                            if i < len(hover_creature.in_scales) and len(hover_creature.in_scales[i]) > brain_length-bsel_line-1\
                                            and hover_creature.in_active[i][brain_length-bsel_line-1] else " " * 5,
                                        ("%5.2f" % hover_creature.intermediate[i]) if len(hover_creature.intermediate) > i else " " * 5,
                                        ("%6.2f" % hover_creature.outs[i]) if len(hover_creature.outs) > i else " " * 6,
                                        creature.outputs[i] if len(creature.outputs) > i else ""))
                    else:
                        bottom_lines.append("%5s %s       %s       %s %s" % (
                                    creature.inputs[i] if len(creature.inputs) > i else " " * 2,
                                    ("%5.2f" % hover_creature.ins[i]) if len(hover_creature.ins) > i else " " * 5,
                                    ("%5.2f" % hover_creature.intermediate[i]) if len(hover_creature.intermediate) > i else " " * 5,
                                    ("%6.2f" % hover_creature.outs[i]) if len(hover_creature.outs) > i else " " * 6,
                                    creature.outputs[i] if len(creature.outputs) > i else ""))
        else:
            labeltext = "Overview"
            infotexts = [
                    ("time ", "%.1fd" % (time / 100), (255, 128, 0), 0),
                    ("population ", "%d" % (population), (255, 0, 255), 0),
                    ("", "[PAUSED]" if paused else "", (0, 128, 255), 0),
                    ("", "TOP CREATURES", (128, 128, 255), 0),
                ]
            top_creatures = sorted([c for c in creatures if c.alive], key=lambda c: c.energy, reverse=True)[:TOP_CREATURES_COUNT]
            for i in range(len(top_creatures)):
                c = top_creatures[i]
                infotexts.append(("%s (%s): " % (c.name, ("%.2fd" % (c.age/100)) if c.alive else "dead"), "%.2fe" % c.energy,
                         (255*(1-(sigmoid(max(MIN_CREATURE_ENERGY, c.energy - MIN_CREATURE_ENERGY)) * 2 - 1)),
                          (sigmoid(max(MIN_CREATURE_ENERGY, c.energy - MIN_CREATURE_ENERGY)) * 2 - 1) * 255, 0), select_creature_by_line, i))

            for i in range(TOP_CREATURES_COUNT - population):
                infotexts.append(("", "", (0,0,0)))

            infotexts += [
                    ("", "", (0,0,0)),
                    ("acts of god", "", (0,0,0)),
                    ("options", "", (0,0,0)),
                    ("fast forward", "", (0,0,0), fast_forward_on, 0),
                    ("exit", "", (0,0,0), exit_sim, 0),
                ]

            #bottom_lines = [ "version 3.141224" ]
            bottom_lines = []
            species_types = {}
            for c in creatures:
                if c.generation > 0 and c.alive and c.extant:
                    ancestor_code = "-".join([c.name for c in c.ancestors])
                    if ancestor_code in species_types:
                        species_types[ancestor_code] += 1
                    else:
                        species_types[ancestor_code] = 1

            species_total = sum(species_types.values()) # total belonging to a 'species'
            species_sorted = []
            for k in species_types.keys():
                species_sorted.append((k, species_types[k], species_types[k] / population * 100))

            species_sorted.sort(key=lambda x: x[1], reverse=True) # sort descending

            for s in species_sorted:
                if s[1] > 1:
                    bottom_lines.append("%s: %.1f%%" % (s[0], s[2]))

            bottom_lines.append("other: %.1f%%" % ((1 - (species_total / population)) * 100))

            draw_pop_graph(win, panel_width)


    label = bigfont.render(labeltext, 0, (255, 255, 255))

    infolabels = []
    infovals = []
    for line in infotexts:
        if line is None:
            continue
        infolabels.append(smallfont.render(line[0], 1, (255, 255, 255)))
        #print(line[0] + str(line[2]))
        try:
            infovals.append(smallfont.render(line[1], 1, line[2]))
        except TypeError:
            print("uh oh, you tried " + str(line[2]) + " for " + line[0] + " but that was bad.")

    win.blit(label, (world_w * draw_scale + panel_margin, panel_vmargin))
    click_callback = None
    for linenum in range(len(infovals)):
        draw_pos = (world_w * draw_scale + panel_margin, panel_vmargin + 35 + lineheight * linenum)
        if linenum == tsel_line and len(infotexts[linenum]) > 3 and infotexts[linenum][3]: # param 3 is a function to be called on click, or 0 if not clickable
            win.fill((50, 50, 50), ((world_w * draw_scale, draw_pos[1]), (panel_width, lineheight)))
            click_callback = infotexts[linenum][3]
            click_callback_arg = infotexts[linenum][4]
        if infotexts[linenum] is not None:
            win.blit(infolabels[linenum], draw_pos)
            win.blit(infovals[linenum], (world_w * draw_scale + panel_margin + smallfont.size(infotexts[linenum][0])[0], panel_vmargin + 35 + lineheight * linenum))

    bottom_texts = []
    for msg in bottom_lines:
        bottom_texts.append(smallfont.render(msg, 1, (255, 255, 255)))
    for i in range(len(bottom_texts)):
        win.blit(bottom_texts[i], (world_w * draw_scale + panel_margin, world_h * draw_scale - panel_margin - (len(bottom_texts) - i) * lineheight))

    pygame.display.flip()

def select_creature_by_line(n):
    global selected_creature, tsel_line
    # Callback for when a creature is clicked in the list of top creatures.
    selected_creature = top_creatures[n]
    tsel_line = None

def select_parent_1(n):
    if current_history_entry is None:
        switch_history_entry(selected_creature.parents[0])
    else:
        switch_history_entry(current_history_entry.parents[0])

def select_parent_2(n):
    if current_history_entry is None:
        switch_history_entry(selected_creature.parents[1])
    else:
        switch_history_entry(current_history_entry.parents[1])

def select_child(n):
    switch_history_entry(current_history_entry.children[n])

def select_ancestor(n):
    switch_history_entry(selected_creature.ancestors[n])

def select_creature_entry(n):
    switch_history_entry(selected_creature.hist_entry)

def switch_history_entry(entry):
    global current_history_entry, new_history_entry
    current_history_entry = entry
    new_history_entry = True

def exit_sim(n):
    global current_page
    current_page = "exit_confirm"

def real_exit(n):
    global done
    done = True

def cancel_exit(n):
    global current_page
    current_page = None

def fast_forward_on(n):
    global fast_forward
    fast_forward = True

def recount_descendants(n):
    current_history_entry.compute_descendants(recount=True)
    for i in current_history_entry.children:
        i.compute_descendants(recount=True)

def calculate_tile_color(x, y):
    if altitude[y][x] > WATER_LEVEL:
        #color = (1 - world[y][x], 1 - world[y][x]/3, 0)
        color = ((1-(worldstate[y][x])) * 0.7 + (altitude[y][x] - 0.25) * 0.7, (0.5+(worldstate[y][x])/0.5) * 0.7 + (altitude[y][x] - 0.25) * 0.7, (altitude[y][x] - 0.25) * 0.7)
    else:
        color = (0, 0.3+altitude[y][x], 1+altitude[y][x])
    return color

def select_line(pos):
    global bsel_line, tsel_line, brain_sel_out, brain_sel_int, brain_sel_inp
    if pos[1] > 3 * world_h * draw_scale // 5:
        bsel_line = (world_h * draw_scale - panel_margin - pos[1]) // lineheight
        tsel_line = None
    else:
        tsel_line = (pos[1] - (panel_vmargin + 35)) // lineheight
        bsel_line = None
    if selected_creature is not None:
        brain_sel_out = False
        brain_sel_int = False
        brain_sel_inp = False
        right = world_w * draw_scale + panel_width - panel_margin
        if right - smallfont.size(" " * 13)[0] < pos[0] and pos[0] < right:
            brain_sel_out = True
        if right - smallfont.size(" " * 26)[0] < pos[0] and pos[0] < right - smallfont.size(" " * 20)[0]:
            brain_sel_int = True
        if right - smallfont.size(" " * 45)[0] < pos[0] and pos[0] < right - smallfont.size(" " * 32)[0]:
            brain_sel_inp = True

def select_creature_by_pos(pos):
    global selected_creature
    selected_creature = point_in_creature(pos)

def log(msg):
    global log_msgs
    log_msgs.append(msg)
    if len(log_msgs) > LOG_LENGTH:
        log_msgs.pop(0)
    if do_print_log:
        print(msg)

def ffdraw(win):
    win.fill((0,0,0))
    text = bigfont.render("%.1fd" % (time / 100), 0, (255,255,255))
    text2 = smallfont.render("Click to exit fast forward.", 0, (255,255,255))
    win.blit(text, (10, 10))
    win.blit(text2, (10, 50))
    draw_pop_graph(win, draw_scale * world_w + panel_width)
    if time % 10 == 0:
        pygame.display.flip()

def draw_pop_graph(win, width):
    recent_history = pop_history[-width:]
    recent_history_max = 30
    if len(recent_history) > 0:
        creature_pop_max = max([x[0] for x in recent_history])
        plant_pop_max = max([x[1] for x in recent_history]) # scaling different
        recent_history_max = max(creature_pop_max, plant_pop_max, 30)

    graph_height = 200
    for i in range(len(recent_history), 0, -1):
        if recent_history[-i][0] > recent_history[-i][1]:
            win.fill((255, 60, 40), ((draw_scale * world_w + panel_width - i, draw_scale * world_h - (recent_history[-i][0] / recent_history_max) * graph_height),
                        (1, (recent_history[-i][0] - recent_history[-i][1]) / recent_history_max * graph_height + 1)))
            win.fill((40, 60, 40), ((draw_scale * world_w + panel_width - i, draw_scale * world_h - (recent_history[-i][1] / recent_history_max) * graph_height),
                        (1, recent_history[-i][1] / recent_history_max * graph_height + 1)))
        elif recent_history[-i][0] < recent_history[-i][1]:
            win.fill((40, 200, 60), ((draw_scale * world_w + panel_width - i, draw_scale * world_h - (recent_history[-i][1] / recent_history_max) * graph_height),
                        (1, (recent_history[-i][1] - recent_history[-i][0]) / recent_history_max * graph_height + 1)))
            win.fill((40, 60, 40), ((draw_scale * world_w + panel_width - i, draw_scale * world_h - (recent_history[-i][0] / recent_history_max) * graph_height),
                        (1, recent_history[-i][0] / recent_history_max * graph_height + 1)))
        else: # equal
            win.fill((40, 60, 40), ((draw_scale * world_w + panel_width - i, draw_scale * world_h - (recent_history[-i][0] / recent_history_max) * graph_height),
                        (1, recent_history[-i][0] / recent_history_max * graph_height + 1)))

clock = pygame.time.Clock()
done = False
paused = False

if __name__ == "__main__":
    altitude, grass = init_world() # actual altitude values for world
    #world = [[z if z > 0 else z for z in x] for x in world]
    plants = []
    init_plants()
    world = [g[:] for g in grass]
    worldstate = [[z * (0.75 + random.uniform(-0.2, 0.2)) if z > 0 else z for z in x] for x in grass]
    creatures = init_creatures()

    pygame.init()

    win = pygame.display.set_mode((world_w * draw_scale + panel_width, world_h * draw_scale), pygame.DOUBLEBUF)
    bigfont = pygame.font.SysFont("monospace", 30, bold=True)
    smallfont = pygame.font.SysFont("monospace", 15, bold=True)
    charwidth, lineheight = smallfont.size("hello")

    # draw landscape only once, to run faster
    landscape = pygame.Surface((world_w * draw_scale, world_h * draw_scale))
    for y in range(len(world)):
        for x in range(len(world[y])):
            color = calculate_tile_color(x, y)
            rightcolor = (max(0, min(255, 255 * color[0])),max(0, min(255, 255 * color[1])),max(0, min(255, 255 * color[2])))

            landscape.fill(rightcolor, ((x*draw_scale, y*draw_scale), (draw_scale, draw_scale)))

    while not done:
        if not fast_forward:
            clock.tick(60)
        else:
            clock.tick(6000)
        if not paused:
            update(creatures, altitude, world, worldstate)
        for p in plants:
            if not p.alive:
                plant_positions[p.tile_pos] = [p for p in plant_positions[p.tile_pos] if p.alive]
        plants = [p for p in plants if p.alive and p.energy > 0]
        plant_population = len(plants)
        creatures = [c for c in creatures if c.extant]
        population = len([c for c in creatures if c.alive])
        if not fast_forward:
            draw(win, landscape, worldstate, altitude, creatures, plants)
        else:
            ffdraw(win)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if current_page != "exit_confirm":
                    current_page = "exit_confirm"
                else:
                    done = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    current_page = None
                    selected_creature = None
                    current_history_entry = None
                if event.key == pygame.K_RETURN:
                    if current_page == "exit_confirm":
                        done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not fast_forward:
                    if pygame.mouse.get_pos()[0] < draw_scale * world_w:
                        select_creature_by_pos((pygame.mouse.get_pos()[0] / draw_scale, pygame.mouse.get_pos()[1] / draw_scale))
                        current_history_entry = None
                        current_page = None
                    elif tsel_line is not None:
                        if click_callback is not None:
                            click_callback(click_callback_arg)
                else:
                    fast_forward = False
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pos()[0] > draw_scale * world_w:
                    select_line(pygame.mouse.get_pos())
                else:
                    bsel_line = None
                    tsel_line = None
                    brain_sel_int = False
                    brain_sel_out = False
                    brain_sel_inp = False

    pygame.quit()
