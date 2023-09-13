import random

test = False
count = 0
while not test:
    curr = random.random()

    shit = curr < 0.001

    if shit:
        print(curr)
        test = True
    count = count + 1


print(count)