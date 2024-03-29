'''
A simple program to test whether the contents of a binary file are random.
This is not a rigorous test and should not be used as a replacement for
more stringent randomness tests like NIST's randomness test suite
or dieharder. It's main advantage is that users can easily see plots
of the distribution of bytes, or ascii/decimal digits derived from
the raw bytes, as well as a calculation of the min-entropy of bytes.

Run with python3 rand_test <filename>

'''

import math
import matplotlib.pyplot as plt
import sys
from x_from_bytes import hex_from_byte, binary_from_byte, digit_from_byte,\
    ascii_from_bytes, randint

def init_hex_dict():
    ret = dict()
    hex_chars = '0123456789abcdef'
    for c in hex_chars:
        ret[c] = 0
    return ret

# returns dictionary with all byte counts
def byte_counts(inf):
    file = open(inf, 'rb')
    counts = {}
    for i in range(256):
        counts[i] = 0
    byte = file.read(1)
    while byte:
        b = ord(byte)
        counts[b] += 1
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

def dice_counts(inf):
    file = open(inf, 'rb')
    counts = {}
    for i in range(1, 7):
        counts[i] = 0
    byte = file.read(6)

    while byte:

        curr = randint(byte, 1, 7)

        counts[curr] += 1

        byte = file.read(6)

    file.close()
    return counts

# return dictionary with ascii character counts
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

# return dictionary with 2-digit decimal numbers counts
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

# return number of changes in binary string
def changes_in_binary_string(s):
    count = 0
    for i in range(len(s) - 1):
        if s[i] != s[i+1]:
            count += 1
    return count

# return number of runs in file (binary)
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

    inf = sys.argv[1]
    # hex counts
    #print('--- hex counts---')
    #counts = hex_counts(inf)
    #print(counts)
    #print()


    # byte counts and min-entropy
    print('--- byte counts---')
    counts = byte_counts(inf)
    # normalize
    _sum = sum(list(counts.values()))
    vals = [v/_sum for v in list(counts.values())]
    plt.bar(range(len(counts)), vals, align='center')
    plt.title('Byte value distribution for {}'.format('even bytes post-SHA-512'))
    plt.xticks(range(len(counts)), list(counts.keys()))
    p = max(counts.values()) / sum(counts.values())
    h_inf = -1 * math.log(p, 2)
    print('estimated min-entropy: {}'.format(h_inf))

#    print('--- dice counts---')
#    counts = dice_counts(inf)
#    _sum = sum(list(counts.values()))
#    vals = [v/_sum for v in list(counts.values())]
#    plt.bar(range(len(counts)), vals)

    # digits
    #counts = digit_counts(inf)
    #fig,ax=plt.subplots()
    #ax.bar(range(len(counts)), list(counts.values()), align='center')
    #fig.suptitle('2-digit number distribution')

    # ascii
    #counts = ascii_counts(inf)
    #fig,ax=plt.subplots()
    #fig.suptitle('ascii distribution')
    #ax.bar(range(len(counts)), list(counts.values()), align='center')

    # runs
    #print('--- runs ---')
    #runs, e_runs = runs(inf)
    #print('runs: {}\nexpected runs: {}'.format(runs, e_runs))
    #percent_diff = 100 * abs(runs - e_runs)/e_runs
    #print('percent difference: {}%'.format(round(percent_diff, 4)))
    #print()

    plt.show()
