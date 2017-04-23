
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
import time

#test
RANDOM_SEED = 42

# Constants defined for database transaction simulation
INTERVAL_TRANSACTION = 0.0001             # Generate new transactions roughly every x seconds
NUM_READ_REQUESTS = 20                # Number of read requests
NUM_WRITE_REQUESTS = 5                 # Number of write requests
SIM_TIME = 50000                        # Simulation time in minutes
NUM_DATA_BLOCKS = 100                   # number of data blocks
LONGEST_READ = 5
LONGEST_WRITE = 10
ROLLBACK_TIME = 3
last_read_write_time = 0

def source(env, writeNumber, readNumber, interval, readCounter, writeCounter):
    """Source generates write transactions randomly"""
    for i in range(writeNumber):
        c1 = invalidDirtyWrite(env, 'WriteTransaction%02d' % i, writeCounter)
        c2 = read(env, 'ReadTransaction%02d' % i, readCounter)
        env.process(c1)
        env.process(c2)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, name, readCounter):
    """Read transaction in one of data blocks, check by time stamp"""
    start = env.now
    print('%7.4f %s: Here I am reading the request' % (start, name))

    with readCounter.request() as req:
        # time takes to write the request, varies
        patience = random.uniform(0, LONGEST_READ)
        # write the request
        yield env.timeout(patience)
        # total time taken to write the request
        end = env.now - start
        last_read_write_time = int(round(time.time() * 1000))
        print('last_read_write_time')
        print (last_read_write_time)


def invalidDirtyWrite(env, name, writeCounter):
    """Write transaction in one of data blocks, check by time stamp"""
    global last_read_write_time
    current_time = int(round(time.time() * 1000))
    start = env.now
    print('%7.4f %s: Here I am writing the request' % (start, name))

    with writeCounter.request() as req:
        # time takes to write the request, varies
        patience = random.uniform(0, LONGEST_WRITE)
        # write the request
        yield env.timeout(patience)
        # total time taken to write the request
        end = env.now - start
        print('current_time')
        print(current_time)

        if last_read_write_time >= current_time:
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
            last_read_write_time = int(round(time.time() * 1000))

# Setup and start the database transaction simulation
print('DataBase Transaction')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start both read and write processes, and run
readCounter = simpy.Resource(env, capacity=1000000000)
writeCounter = simpy.Resource(env, capacity=1000)
env.process(source(env, NUM_WRITE_REQUESTS, NUM_READ_REQUESTS, INTERVAL_TRANSACTION, readCounter, writeCounter))
env.run()
#env.run(until = 100) #total simulation time is set to 100 time unit
