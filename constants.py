# CONSTANTS
# =========

# VALUES
MIN_CREATURE_ENERGY = 0.1   # energy level below which a creature dies
HP_HALF_E_LEVEL = 3         # energy level which gives 50% of max possible HP recovery
MAX_NATURAL_CORPSE_AGE = 40 # frames a corpse stays around after dying of starvation
MAX_CORPSE_AGE = 130        # frames a corpse stays around after being MURDERED

# LIVING
BE_ALIVE_RATIO_COST = 0.001 # as a fraction of total E
BE_ALIVE_COST = 0.001       # as a raw number - both are applied!
TREAD_WATER_COST = 0.002

# MOVING
MOVE_SPEED = 0.4            # speed per unit of speed
MOVE_COST = 0.005           # cost per unit of speed
TURN_SPEED = 15             # speed of turning
TURN_COST = 0.002           # cost per unit of turning

# REPRODUCING
SEX_REQ = 0.2               # energy requirement to sexually reproduce          # formerly 2.0
SEX_COST = 0.8              # energy cost to sexually reproduce                 # formerly 1.8
SEX_COOLDOWN = 20           # non-reproduction time after sexually reproducing  # formerly 40
SEX_THRESHOLD = 0.0         # min. birth factor to sexually reproduce           # formerly 0.5
ASEX_REQ = 0.5              # energy requirement to asexually reproduce         # formerly 2.5
ASEX_COST = 0.3             # energy cost to asexually reproduce                # formerly 2.3
ASEX_COOLDOWN = 30          # non-reproduction time after asexually reproducing # formerly 60
ASEX_THRESHOLD = 0.0        # min. birth factor to asexually reproduce          # formerly 1

# LOOKING
MAX_LOOK_DISTANCE = 10      # maximum distance ahead of themselves creatures can look

# FIGHTING
FIGHT_COST = 10             # cost for max fightingness
FIGHT_RATIO = 0.6           # % of target's HP depleted at maximum fightingness

# EATING
EAT_COST = 0.1              # energy used per unit of tree attempted to eat
MEAT_EAT_COST = 0.05        # energy used per unit of meat attempted to eat
EAT_SPEED = 0.5             # amount of tree eaten per unit of eating
EAT_RATIO = 1.5             # energy per unit of tree digested
MEAT_EAT_RATIO = 35         # energy per E of meat
MEAT_POISON_CUTOFF = 0.25   # M%E at which meat actually hurts you
VEG_POISON_CUTOFF = 0.85    # M%E at which tree actually hurts you

# ENVIRONMENT
WATER_LEVEL = 0
GRASS_GROW_RATE = 0.0004
PLANT_REPRODUCTIVE_THRESHOLD = 10
MAX_PLANTS = 5000
INITIAL_PLANT_NUMBER = 7

# LOGGING
NOTABLE_AGE = 150   # frames age to report when died of starvation
LOG_LENGTH = 30
TOP_CREATURES_COUNT = 15
