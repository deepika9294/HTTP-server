import threading
from _thread import *
a = 1

def new_func(a):
    print("new_func: {}, which is :{}".format(a,i))
    a=a+1


def threading(a,i):
    print("thread: {} which is {}".format(a,i))
    a = a+1
    s = new_func(a)


def create(a):
    # a = 0
    # print(a)
    for i in range(0,5):
        start_new_thread(threading,(a,i)) 
        print("ad")
    # start_new_thread(threading,(a,))



if __name__ == "__main__":
    create(a)