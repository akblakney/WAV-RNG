'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen, set_param_bool
from my_exception import MyException
from generator import query_blocks, generate_from_wav
import secrets
from x_from_bytes import digits_from_bytes, ascii_from_bytes, binary_from_bytes,\
    hex_from_bytes
from rand_utils import display, fold_bytes
import math
from aes_prng import aes_prng

def aes_whiten(b: bytearray):

    seed = b[:48]
    b = b[64:]  # start at second block now, discard first
    key = seed[:32]
    iv = seed[32:48]

    # figure out how many 16-byte blocks needed
    n = len(b)
    num_blocks = math.ceil(n // 16)
    aes_out = aes_prng(key, iv, num_blocks)
    assert(len(aes_out) >= n)
    
    # xor
    xor = bytes(a^b for (a,b) in zip(b, aes_out[:n]))
    return xor


# prints out the help statement
def my_help():
    with open('help') as f:
        lines = f.readlines()
        for l in lines:
            print(l,end='')

# return params from command line arguments
def set_params():
    # get args
    inf = set_param_gen(sys.argv, '--in', None, \
        'valid filename must follow --in flag.')

    start = set_param_int(sys.argv, '-s', 0)
    end = set_param_int(sys.argv, '-e', None)
    no_sha = set_param_bool(sys.argv, '--no-sha')
    header_len = set_param_int(sys.argv, '--header-len', 100)
    block_size = set_param_int(sys.argv, '--block-size', 2048)
    fold = set_param_bool(sys.argv, '--fold')
    aes = set_param_bool(sys.argv, '--aes')


    # set data mode
    data_mode = None
    if '--ascii' in sys.argv:
        data_mode = 'ascii'
    elif '--binary' in sys.argv:
        data_mode = 'binary'
    elif '--hex' in sys.argv:
        data_mode = 'hex'
    elif '--digits' in sys.argv:
        data_mode = 'digits'

    # set output filename
    outf = set_param_gen(sys.argv, '--out', None,\
        'valid filename must follow --out flag.')

    # option for blake
    hash_function = 'sha512'
    if '--blake' in sys.argv:
        hash_function = 'blake2b'

    return inf, start, end, data_mode, outf, no_sha, header_len, \
        block_size, fold, aes, hash_function


if __name__ == '__main__':

    # help
    if '-h' in sys.argv or '--help' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, data_mode, outf, no_sha, header_len, \
        block_size, fold, aes, hash_function = set_params()

    # not in help mode, because already quit, so must be regular or query mode
    # make sure filename is given
    if inf is None:
        raise MyException('No filename given. Provide file with --in <filename>')

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        filesize = os.path.getsize(inf)
        available_blocks = query_blocks(filesize, block_size, header_len)
        print('available 64-byte blocks for {} with block-size {}: {}'.format(
            inf, block_size, available_blocks))
        exit()

    # now we are reading wav file and generate the bytearray from it
    ret = generate_from_wav(inf, block_size=block_size, start=start, end=end, \
        header_len=header_len, no_sha=no_sha, hash_function=hash_function)

    # perform fold step if applicacable
    if fold:
        ret = fold_bytes(ret)

    # perform aes whitening if applicable
    # hard code aes values here ...
    if aes:
        ret = aes_whiten(ret)
        
        

    num_bytes = len(ret)

    if '--secrets' in sys.argv:
        s = secrets.token_bytes(num_bytes)
        ret = bytes(a^b for (a,b) in zip(ret, s))

    
    # print or write to file
    display(ret, data_mode, outf)


