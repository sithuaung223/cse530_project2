
"""
LAB 02_part_b
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
INTERVAL_TRANSACTION = 10             # Generate new transactions roughly every x seconds
NUM_READ_REQUESTS = 100               # Number of read requests
NUM_WRITE_REQUESTS = 10                # Number of write requests
SIM_TIME = 50000                        # Simulation time in minutes
NUM_DATA_BLOCKS = 50                   # number of data blocks
datablockStates = [ ]   # Keeps track of the locks on the 100 different datablocks
LONGEST_READ = 1
LONGEST_WRITE = 3
ROLLBACK_TIME = 1
last_read_write_time = 0
writenum = 0
invalidwritenum = 0

def source(env, writeNumber, readNumber, interval, readCounter, writeCounter):
    """Source generates write transactions randomly"""
    for i in range(NUM_DATA_BLOCKS):
        c1 = invalidDirtyWrite(env, 'WriteTransaction%02d' % i, writeCounter, readCounter)
        c2 = read(env, 'ReadTransaction%02d' % i, readCounter)
        env.process(c1)
        env.process(c2)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, name, readCounter):
    global last_read_write_time
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


def invalidDirtyWrite(env, name, writeCounter, readCounter):
    """Write transaction in one of data blocks, check by time stamp"""
    global last_read_write_time
    global writenum
    global invalidwritenum
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

        if last_read_write_time > current_time:
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
            last_read_write_time = int(round(time.time() * 1000000))
            invalidwritenum +=1
        else:
            writenum +=1

    # Create more transactions while the simulation is running
    i = 0
    while True and i < 100:
        yield env.timeout(random.randint(INTERVAL_TRANSACTION-2, INTERVAL_TRANSACTION+2))
        i += 1
        data_value = random.randint(0, NUM_DATA_BLOCKS)
        read_or_write = random.random()
#        env.process(read(env, 'ReadTransaction%02d' % i, readCounter))

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

percent = (invalidwritenum/writenum)*100
print('total write number: %d, invalid write number: %d. The percent of invalid write is %.3f %%.' %(writenum,invalidwritenum,percent))
