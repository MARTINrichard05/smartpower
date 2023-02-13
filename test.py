import time

while True:
    before = time.time()
    print(before)
    time.sleep(10)
    after = time.time()
    print(after)

    print(after-before)

    if (after - before) > 12:
        print('hehe')