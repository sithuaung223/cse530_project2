
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

#test
RANDOM_SEED = 42

# Constants defined for database transaction simulation
NUM_READ_REQUESTS = 2000                # Number of read requests
NUM_WRITE_REQUESTS = 50                 # Number of write requests
SIM_TIME = 50000                        # Simulation time in minutes
NUM_DATA_BLOCKS = 100                   # number of data blocks
LONGEST_READ = 5
LONGEST_WRITE = 10
ROLLBACK_TIME = 3

def source(env, number, readCounter, writeCounter):
    """Source generates write transactions randomly"""
    for i in range(number):
        c = invalidDirtyWrite(env, 'WriteTransaction%02d' % i, readCounter, writeCounter)
        env.process(c)

def invalidDirtyWrite(env, name, readCounter, writeCounter):
    """Write transaction in one of data blocks, check by time stamp"""
    start = env.now
    last_read_write_time = 0
    print('%7.4f %s: Here I am writing the request' % (start, name))

    with writeCounter.request() as req:
        # time takes to write the request, varies
        patience = random.uniform(0, LONGEST_WRITE)
        # write the request
        yield env.timeout(patience)
        # total time taken to write the request
        end = env.now - start

        if last_read_write_time > start:
        # re-attempt the write transaction
            print('the write is invalidated, reattempting')
            # rollback the transaction, start the transaction again
            start = env.now
            yield env.timeout(ROLLBACK_TIME)
            print('%7.4f %s: Here I am re-writing the request' % (start, name))
            # time takes to write the request, varies
            patience = random.uniform(0, LONGEST_WRITE)
            # write the request
            yield env.timeout(patience)
            # total time taken to write the request
            end = env.now - start

# Setup and start the database transaction simulation
print('DataBase Transaction')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start both read and write processes, and run
readCounter = simpy.Resource(env, capacity=1000000000)
writeCounter = simpy.Resource(env, capacity=1000)
env.process(source(env, NUM_WRITE_REQUESTS, readCounter, writeCounter))
env.run()
#env.run(until = 100) #total simulation time is set to 100 time unit
