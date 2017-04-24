import random
import simpy

RANDOM_SEED = 42
NUM_DATA = 1  
READTIME = 2      # Minutes it takes to read 
WRITETIME = 4      # Minutes it takes to write 
T_INTER = 3       # Create a read/write every ~4 minutes
SIM_TIME = 50     # Simulation time in minutes

#READ = 0
#WRITE = 1
write_lock = False

class readWrite(object):

  def __init__(self, env, num_data, readTime, writeTime):
    self.env = env
    self.db = simpy.PriorityResource(env, num_data)
    self.readTime = readTime
    self.writeTime = writeTime
  def read(self):
    yield self.env.timeout(self.readTime)
  def write(self):
    yield self.env.timeout(self.writeTime)


def reader(env, name, rw, rank):
  reqTime = env.now
  print('%.2f %s: Request ' % (reqTime, name))
  with rw.db.request(priority = rank) as req:
    results = yield req | env.timeout(10)
    if req in results:
      print('%.2f %s: Start ' % (env.now, name))
      yield env.process(rw.read())
      print('%.2f %s: Finish ' % (env.now, name))

    else:
      print('%.2f %s: Starving.... ' % (env.now, name))
      with rw.db.request(priority = rank-1) as req: #move rank up to start a job
        waitTime = env.now - reqTime
        print('%.2f %s: Start:Waited %.2f ...' % (env.now, name, waitTime))
        yield env.process(rw.read())
        print('%.2f %s: Finish ' % (env.now, name))


def writer(env, name, rw, rank):
  global write_lock
  reqTime = env.now
  print('%.2f %s: Request ' % (reqTime, name))
  with rw.db.request(priority = rank) as req:
    yield req
    print('%.2f %s: Start ' % (env.now, name))
    yield env.process(rw.write())
    print('%.2f %s: Finish ' % (env.now, name))
  write_lock = False
    

def setup(env, num_data, readTime, writeTime, t_inter):
  global write_lock
  #create readWrite
  readwrite = readWrite(env, num_data, readTime, writeTime)
  
  #create 4 initial readers
  for i in range(4):
    env.process(reader(env, 'Reader%d' % i, readwrite, 1))
  i = i+1
  env.process(writer(env, 'Writer%d' % i, readwrite, 0))
  write_lock = True

  # Create more readers/writers while the simulation is running
  while True:
    yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
    i += 1
    rank = random.randrange(0,2)
    if (rank is 0): 
      if (write_lock is False): #Writer turn
        write_lock = True
        env.process( writer(env, 'Writer%d' % i, readwrite, rank))
      else: #Reader turn but change rank 0 to 1
        env.process( reader(env, 'Reader%d' % i, readwrite, rank+1))
    else: #Reader turn
        env.process( reader(env, 'Reader%d' % i, readwrite, rank))
    #if (request is READ):
    #  env.process( reader(env, 'Reader%d' % i, readwrite))
    #elif (request is WRITE):
    #  env.process( writer(env, 'Writer%d' % i, readwrite))


# Main
# Setup and start the simulation
print('Typical Read/Write')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env, NUM_DATA, READTIME, WRITETIME, T_INTER))

# Execute!
env.run(until=SIM_TIME)
