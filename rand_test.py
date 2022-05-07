import math
import matplotlib.pyplot as plt
import sys
from x_from_bytes import hex_from_byte, binary_from_byte, digit_from_byte,\
    ascii_from_bytes

def init_hex_dict():
    ret = dict()
    hex_chars = '0123456789abcdef'
    for c in hex_chars:
        ret[c] = 0
    return ret

def byte_counts(inf):
    file = open(inf, 'rb')
    counts = {}
    byte = file.read(1)
    while byte:
        b = ord(byte)
        if b in counts:
            counts[b] += 1
        else:
            counts[b] = 1
        byte = file.read(1)
    file.close()
    return counts

# read binary data file, return dictionary giving
# counts of each hexadecimal character
def hex_counts(inf):
    file = open(inf, 'rb')
    counts = init_hex_dict()
    byte = file.read(1)

    while byte:

        curr_hex = hex_from_byte(ord(byte))

        counts[curr_hex[0]] += 1
        counts[curr_hex[1]] += 1

        byte = file.read(1)

    file.close()
    return counts

def ascii_counts(inf):
    file = open(inf, 'rb')
    byte = file.read(1)
    counts = {}
    while byte:
        curr = ascii_from_bytes([ord(byte)])
        if curr != '':
            if curr in counts:
                counts[curr] += 1
            else:
                counts[curr] = 1
        byte = file.read(1)
    file.close()
    return counts

def digit_counts(inf):
    file = open(inf, 'rb')
    byte = file.read(1)
    counts = {}
    while byte:
        curr_dig = digit_from_byte(ord(byte))
        if curr_dig is not None:
            if curr_dig in counts:
                counts[curr_dig] += 1
            else:
                counts[curr_dig] = 1
        byte = file.read(1)
    file.close()
    return counts

def changes_in_binary_string(s):
    count = 0
    for i in range(len(s) - 1):
        if s[i] != s[i+1]:
            count += 1
    return count

def runs(inf):
    file = open(inf, 'rb')
    change_count = 0
    byte = file.read(1)
    prev_char = 'x'
    index = 1
    while byte:
        curr_bin = binary_from_byte(ord(byte))
        change_count += changes_in_binary_string(curr_bin)
        
        # also add to see if there is a change from prev
        if curr_bin[0] == prev_char:
            change_count += 1
        prev_char = curr_bin[-1]

        byte = file.read(1)
        index += 1

    runs = 1 + change_count
    expected_runs = 1 + (8*index - 1) * 0.5
    file.close()
    return runs, expected_runs


if __name__ == '__main__':

    #inf = './rand/noise8.rand'
    inf = sys.argv[1]
    # hex counts
    print('--- hex counts---')
    counts = hex_counts(inf)
    print(counts)
    print()
    #plt.bar(range(len(counts)), list(counts.values()), align='center')
    #plt.xticks(range(len(counts)), list(counts.keys()))


    # byte counts
    print('--- byte counts---')
    counts = byte_counts(inf)
    plt.bar(range(len(counts)), list(counts.values()), align='center')
    plt.title('Byte value distribution')
    #plt.xticks(range(len(counts)), list(counts.keys()))
    p = max(counts.values()) / sum(counts.values())
    h_inf = -1 * math.log(p, 2)
    print('estimated min-entropy: {}'.format(h_inf))

    # digits
    counts = digit_counts(inf)
    fig,ax=plt.subplots()
    ax.bar(range(len(counts)), list(counts.values()), align='center')
    fig.suptitle('2-digit number distribution')

    # ascii
    counts = ascii_counts(inf)
    fig,ax=plt.subplots()
    fig.suptitle('ascii distribution')
    ax.bar(range(len(counts)), list(counts.values()), align='center')

    # runs
    print('--- runs ---')
    runs, e_runs = runs(inf)
    print('runs: {}\nexpected runs: {}'.format(runs, e_runs))
    percent_diff = 100 * abs(runs - e_runs)/e_runs
    print('percent difference: {}%'.format(round(percent_diff, 4)))
    print()
    plt.show()
