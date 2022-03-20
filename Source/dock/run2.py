import time

name = "2"

for i in range(100):
    print(2)
    f = open("b.txt", "w+")
    f.write(str(time.time())+"_2_\n")
    f.close()
    time.sleep(1)
