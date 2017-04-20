
"""
LAB 02
Scenario:
    In this lab, please use SimPy to simulate database transaction reading and writing.
    Your project should randomly generate read and write events that will read or write
    a set of data for a period of time.

    The simulation times, number of data blocks, and
    longest read or write time period are set at the beginning of the simulation.

    The simulation time needs to be at least 2xnumber of data blocks x longest read or write time
"""
import random
import simpy

RANDOM_SEED = 42
NEW_CUSTOMERS = 5  # Total number of customers
INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience

# Constants defined for database transaction simulation
NUM_READ_REQUESTS = 2000             # Number of machines in the carwash
NUM_WRITE_REQUESTS = 50            # Minutes it takes to clean a car
T_INTER = 7                         # Create a car every ~7 minutes
SIM_TIME = 50000                    # Simulation time in minutes
NUM_DATA_BLOCKS = 100                # number of data blocks
LONGEST_READ = 5
LONGEST_WRITE = 10

def source(env, number, interval, readCounter, writeCounter):
    """Source generates customers randomly"""
    for i in range(number):
        c = customer(env, 'Customer%02d' % i, readCounter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def customer(env, name, readCounter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print('%7.4f %s: Here I am' % (arrive, name))

    with readCounter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the readCounter or abort at the end of our tether
        results = yield req | env.timeout(patience)

        wait = env.now - arrive

        if req in results:
            # We got to the readCounter
            print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now, name))

        else:
            # We reneged
            print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))

def simulateDataBase(env, number, interval, readCounter):
    """simulateDataBase generates database transaction randomly"""
    for i in range(number):
        c = customer(env, 'Customer%02d' % i, readCounter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


# Setup and start the database transaction simulation
print('DataBase Transaction')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start both read and write processes, and run
readCounter = simpy.Resource(env, capacity=1000000000)
writeCounter = simpy.Resource(env, capacity=1000)
env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, readCounter, writeCounter))
env.run()
