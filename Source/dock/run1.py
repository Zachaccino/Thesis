import time

name = "1"

for i in range(100):
    print(1)
    f = open("a.txt", "w+")
    f.write(str(time.time())+"_1_\n")
    f.close()
    time.sleep(1)
