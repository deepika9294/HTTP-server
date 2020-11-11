import os
import sys

if __name__ == "__main__":
    # default port if user doesnt enter eny port number
    if(len(sys.argv) < 2): 
        port = 9000
    else:
        port = sys.argv[0]
    
    os.system("python3 myserver.py {}".format(port))