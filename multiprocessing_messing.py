import multiprocessing
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def reset():
    r.set('qty_bought', 0)

def get_qty_bought():
    return int(r.get('qty_bought'))

def inc_qty_bought(inc):
    return int(r.incr('qty_bought', inc))

reset()

# def worker(num):
#     print 'Worker: ', num
#     return
# 
# for i in range(5):
#     jobs = []
#     p = multiprocessing.Process(target=worker, args=(i,))
#     jobs.append(p)
#     p.start()


