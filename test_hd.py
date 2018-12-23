from random import randint
import sys
print('This will write to ' + sys.argv[1])
if input('OK? [y, N] ') != 'y':
    exit()

print('Running...')
f = open(sys.argv[1], 'r+b')
e = f.seek(0, 2)
e /= 4096
e -= 1

data = []
for i in range(4096):
    data.append(randint(0,255))
data = bytes(data)

secs=[]
for i in range(10000):
    p = randint(0, e)
    secs.append(p)
    f.seek(p * 4096)
    f.write(data)
    f.flush()

for s in secs:
    f.seek(s * 4096)
    if f.read(4096) != data:
        print(f'Error sector {s}')

f.close()
print('Done')
