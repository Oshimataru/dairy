import threading
import time

lock=threading.Lock()
def cube(number):
    with lock:
        number = number * number * number
        print(number)
        # time.sleep(10)
    
starttime=time.time()
t1=threading.Thread(target=cube(10))
endtime=time.time()
t2=threading.Thread(target=cube(10))

t1.start()
t2.start()
t1.join()
t2.join()
print(endtime-starttime)
