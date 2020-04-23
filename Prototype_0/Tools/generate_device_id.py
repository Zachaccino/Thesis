import random
import string

def generate_id(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

print(generate_id(16))