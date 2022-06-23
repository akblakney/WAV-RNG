'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen, set_param_bool
from my_exception import MyException
from generator import BaseGenerator, SecretsGenerator, ExtendGenerator

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
    extension_rounds = set_param_int(sys.argv, '--extend', None)
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
        extension_rounds, block_size


if __name__ == '__main__':

    # help
    if '-h' in sys.argv or '--help' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, data_mode, outf, no_sha, header_len, \
        extension_rounds, block_size = set_params()

    # not in help mode, because already quit, so must be regular or query mode
    # make sure filename is given
    if inf is None:
        raise MyException('No filename given. Provide file with --in <filename>')


    # add the WAV ExtendGenerator
    e = ExtendGenerator(inf, start, end, header_len, no_sha, extension_rounds, block_size)

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        available_blocks = e.query()
        print('available 64-byte blocks for {} with block-size {}: {}'.format(
            inf, block_size, available_blocks))
        exit()

    # create base generator and add additional ones
    base = BaseGenerator()

    num_bytes = e.num_blocks * 64 # number of bytes per block
    base.add_generator(e)

    if '--secrets' in sys.argv:
        base.add_generator(SecretsGenerator(num_bytes))

    # generate
    base.generate()

    # print or write to file
    base.display(data_mode, outf)


