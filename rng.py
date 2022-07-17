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

 # writes or prints self.data in desired format
def display(wav_bytes, data_mode, outf):

    # get data to write
    write_mode = 'w'
    if data_mode is None:
        ret = wav_bytes
        write_mode = 'wb'
    elif data_mode == 'ascii':
        ret = ascii_from_bytes(wav_bytes)
    elif data_mode == 'binary':
        ret = binary_from_bytes(wav_bytes)
    elif data_mode == 'hex':
        ret = hex_from_bytes(wav_bytes)
    elif data_mode == 'digits':
        ret = digits_from_bytes(wav_bytes)

    # write or print
    if outf is None:
        print(ret)
    else:
        with open(outf, write_mode) as f:
            f.write(ret)        

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

    return inf, start, end, data_mode, outf, no_sha, header_len, \
        block_size


if __name__ == '__main__':

    # help
    if '-h' in sys.argv or '--help' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, data_mode, outf, no_sha, header_len, \
        block_size = set_params()

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

    # now we are reading wav file
    ret = generate_from_wav(inf, block_size, start, end, header_len, no_sha)

    num_bytes = len(ret)

    if '--secrets' in sys.argv:
        s = secrets.token_bytes(num_bytes)
        ret = bytes(a^b for (a,b) in zip(ret, s))

    
    # print or write to file
    display(ret, data_mode, outf)


