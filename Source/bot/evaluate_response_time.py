from settings import REQ_COUNT, DEV_COUNT

f = open("mcu_ids", "r")
id_pool = f.readline().split(",")
f.close()

res = [[] for _ in range(REQ_COUNT)]

# Return a CSV showing the average response time for each backend access.
for i in range(DEV_COUNT):
    f = open("./results/"+id_pool[i], "r")
    lines = f.readlines()
    f.close()
    lines.pop(0)
    for j, l in enumerate(lines):
        res[j].append(float(l.split(",")[1]))


avg_res = []

for r in res:
    avg_res.append(sum(r)/len(r))

f = open("./graphs/response_time.csv", "w")
f.write("Access,AVG. Response Time\n")

for i, r in enumerate(avg_res):
    f.write(str(i) + "," + str(r) + "\n")