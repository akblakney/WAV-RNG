'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen, set_param_bool
from generator import query_blocks, generate_from_wav
import secrets
from x_from_bytes import digits_from_bytes, ascii_from_bytes, binary_from_bytes,\
    hex_from_bytes
from rand_utils import display, fold_bytes
import math

BLAKE_KEY_SIZE = 64

def aes_whiten(b: bytearray):

    from aes_prng import aes_prng

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
    no_hash = set_param_bool(sys.argv, '--no-hash')
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
    blake_key = b''
    if '--blake' in sys.argv:
        hash_function = 'blake2b'

        # option for key
        if '--key-hex' in sys.argv:
            ind = sys.argv.index('--key-hex')
            blake_key = bytes.fromhex(sys.argv[ind + 1])
            if len(blake_key) != BLAKE_KEY_SIZE:
                raise BaseException('blake key must be {} bytes'.format(BLAKE_KEY_SIZE))
        elif '--key-file' in sys.argv:
            ind = sys.argv.index('--key-file')
            key_inf = sys.argv[ind + 1]
            keyfile_size = os.path.getsize(key_inf)
            if keyfile_size < BLAKE_KEY_SIZE:
                raise BaseException(
                    'specified key file is less than required {} bytes'.format(BLAKE_KEY_SIZE))
            f = open(key_inf, 'rb')
            blake_key = f.read(BLAKE_KEY_SIZE)
            f.close()

    return inf, start, end, data_mode, outf, no_hash, header_len, \
        block_size, fold, aes, hash_function, blake_key


if __name__ == '__main__':

    # help
    if '-h' in sys.argv or '--help' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, data_mode, outf, no_hash, header_len, \
        block_size, fold, aes, hash_function, blake_key = set_params()

    # not in help mode, because already quit, so must be regular or query mode
    # make sure filename is given
    if inf is None:
        raise BaseException('No filename given. Provide file with --in <filename>')

    # query for how many bytes can be generated
    if '-q' in sys.argv or '--query' in sys.argv:
        filesize = os.path.getsize(inf)
        available_blocks = query_blocks(filesize, block_size, header_len)
        print('available 64-byte blocks for {} with block-size {}: {}'.format(
            inf, block_size, available_blocks))
        exit()

    # now we are reading wav file and generate the bytearray from it
    ret = generate_from_wav(inf, block_size=block_size, start=start, end=end, \
        header_len=header_len, no_hash=no_hash, hash_function=hash_function, \
        blake_key=blake_key)

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


