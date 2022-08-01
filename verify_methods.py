'''
This file contains methods that can be used to do simple checks
to catch .wav files that are not suitable for use with the MixGenerator/RNG.

This should NOT be a substituted for more rigorous testing, including but not
limited to the ENT program, NIST 800-90b tests for i.i.d.-ness, compression
tests to determine entropy, and so on.

'''

import math
import matplotlib.pyplot as plt
from hashlib import sha256
from scipy.stats import chisquare
from my_exception import MyException

# num_blocks gives number of blocks to look through
# returns proportion of blocks that are unique, i.e. proportion of blocks
# that were NOT collisions
def start_collisions(inf, collision_size, header_len, block_size, num_blocks, \
    only_odd=False, only_even=False):
    if collision_size > block_size:
        raise MyException('collision size must be smaller than block size')
    f = open(inf, 'rb')
    _ = f.read(header_len)
    b = f.read(block_size)

    i = 0
    l = []
    while i < num_blocks and b:

        if only_odd:
            b = bytes([b[i] for i in range(1, len(b), 2)])
        if only_even:
            b = bytes([b[i] for i in range(0, len(b), 2)])
        l.append(b[:collision_size])

        b = f.read(block_size)
        i += 1

    #return (len(l) - len(set(l))) / len(l)
    return len(set(l)) / len(l)

# return an estimate of the min-entropy, in bits/byte given a distribution
# of bytes in dictionary form
def min_entropy_from_byte_dist(b):
    p = max(b.values()) / sum(b.values())
    return -1 * math.log(p, 2)


def odd_byte_dist_from_file(inf):
    return byte_dist_from_file(inf, header_len=101, use_even=True, suppress=True)

# return byte distribution in dictionary form of the even bytes from inf
# returns dicitonary with byte_value -> count
# i.e. gives the distribution of byte values
# inf is input file from which only the EVEN bytes
# are considered
# suppress suppresses odd warning
def byte_dist_from_file(inf, header_len=100, use_even=True, suppress=False):

    if header_len % 2 != 0 and not suppress:
        print('warning: odd header length means odd bytes will be used')
    f = open(inf, 'rb')

    # initialize dict
    ret = {}
    for i in range(256):
        ret[i] = 0

    # skip header
    _ = f.read(header_len)
    
    # populate dict
    b = f.read(1)
    while b:
        ret[ord(b)] += 1
        
        # skip odd byte
        if use_even:
            s = f.read(1)
            if not s:
                break
        b = f.read(1)
    f.close()
    return ret


# given a byte distribution in dictionary form, return
# list with normalized values, i.e. probabilities that sum to 1
def normalize_dist_to_list(dist):
    vals = list(dist.values())
    _sum = sum(vals)
    return [v / _sum for v in vals]


# plot byte distribution given dictionary giving distribution
def plot_byte_dist(byte_dist, ax):
    
    # normalize
    vals_list = normalize_dist_to_list(byte_dist)

    # plot
    ax.bar(range(len(vals_list)), vals_list, align='center')



# given input file inf, count the number of collisions of n-byte blocks
# e.g., for n = 64, count the number of unique 64-byte blocks, considering
# the 64-byte blocks sequentially in the file, and subtract this amount from the total
# number of blocks. The value should always be
# zero for such a large block size, since if the .wav file has sufficient entropy
# 64-byte blocks should never repeat. (64 bytes is 512 bits which is over 10e154,
# a number so large that we should never have any collisions)

# if n > 32, then SHA-256 will be used, as collisions are extremely unlikely
# and this helps performance
def collision_blocks(inf, n, use_even):
    f = open(inf, 'rb')

    l = []
    if use_even:
        chunk = f.read(2*n)
        chunk = bytes([chunk[i] for i in range(0, 2*n, 2)])
    else:
        chunk = f.read(n)
    while chunk:
        if len(chunk) > 32:
            chunk = sha256(chunk).digest()
        l.append(chunk)
        if use_even:
            chunk = f.read(2*n)
            if not chunk or len(chunk) < 2*n:
                break
            chunk = bytes([chunk[i] for i in range(0, 2*n, 2)])
        else:
            chunk = f.read(n)

    # l is populated
    tot = len(l)
    unique = len(set(l))

    f.close()
    return tot - unique

# given byte dist in dictionary form, compute chi squared test statistic
def chi_squared(dist):
    l = list(dist.values())
    return chisquare(l, ddof=0)
