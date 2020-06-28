# This file is used to generate a set of MCU IDs for the bot to use.
import random
import string


# Generate IDs.
def rand_id():
    return 'SIM' + ''.join(random.choice(string.ascii_letters + "1234567890") for _ in range(5))


ids = [rand_id() for _ in range(10000)]
f = open("mcu_ids", "w+")
f.write(','.join(ids))
f.close()

# Generate Regions.
regions = ["Sydney",
           "Kiama",
           "Port Stephens",
           "Auburn",
           "Penrith",
           "Camperdown",
           "Gerringong",
           "Jervis Bay"
           ]

f = open("mcu_regions", "w+")
f.write(','.join(regions))
f.close()
