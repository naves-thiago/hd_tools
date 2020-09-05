from random import randint
import sys

sector_size = 512
write_count = 10000

f = open(sys.argv[1], 'rb')
e = f.seek(0, 2)
f.close()
print('This will write to %s (size: %d B [%.2f TB])' % (sys.argv[1], e, e / (1000**4)))
if input('OK? [y, N] ') != 'y':
    exit()

print('Running...')
f = open(sys.argv[1], 'r+b')
e = f.seek(0, 2)
e /= sector_size
e -= 1

data = []
for i in range(sector_size):
    data.append(randint(0, 255))
data = bytes(data)

print("Writting...")
secs=[]
for i in range(write_count):
    p = randint(0, e)
    secs.append(p)
    try:
        f.seek(p * sector_size)
    except Exception as e:
        print('Seek %d failed with exeption: %s' % (p * sector_size, str(e)))
        break

    try:
        f.write(data)
    except Exception as e:
        print('Write %d failed with exeption: %s' % (p * sector_size, str(e)))
        break

    try:
        f.flush()
    except Exception as e:
        print('Flush %d failed with exeption: %s' % (p * sector_size, str(e)))
        break

    if i % (write_count / 10) == 0:
        print('%d/%d' % (int(i / (write_count / 10)), 10))

print('10/10')
print("Reading...")
read_count = len(secs)
for i in range(read_count):
    s = secs[i]
    try:
        f.seek(s * sector_size)
    except Exception as e:
        print('Seek %d failed with exeption: %s' % (s * sector_size, str(e)))
        break

    try:
        if f.read(sector_size) != data:
            print(f'Error sector {s}')
    except Exception as e:
        print('Read %d failed with exeption: %s' % (s * sector_size, str(e)))
        break

    if i % (read_count / 10) == 0:
        print('%d/%d' % (int(i / (read_count / 10)), 10))

print('10/10')
f.close()
print('Done')
