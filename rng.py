'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen
from my_exception import MyException
from generator import BaseGenerator, SecretsGenerator, GRCGenerator, WAVGenerator

# prints out the help statement
def my_help():
    with open('help') as f:
        lines = f.readlines()
        for l in lines:
            print(l,end='')

# return params from command line arguments
def set_params():
    # get args
    inf = set_param_gen(sys.argv, '--in', None)
    header_len = 100
    bpb = None
    available_bytes = None
    start = None
    end = None
    use_bit = None
    num_bytes = set_param_int(sys.argv, '--num_bytes', None)
    extract = False

    if not inf is None:
        filesize = os.path.getsize(inf)
    
        bpb = set_param_int(sys.argv, '-bpb', 16)
        if bpb % 16 != 0:
            raise MyException('bits per block must be multiple of 16')
        if bpb < 16:
            raise MyException('bits per block must be at least 16')

        available_bytes = (filesize - header_len) // bpb
        start = set_param_int(sys.argv, '-s', 0)
        end = set_param_int(sys.argv, '-e', available_bytes)

        use_bit = set_param_int(sys.argv, '-u', None)
        num_bytes = end - start

    if inf is None and num_bytes is None:
        raise MyException('No input wav file or num_bytes given')
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

    # extraction
    if '--extract' in sys.argv:
        extract = True

    # set output filename
    outf = set_param_gen(sys.argv, '--out', None)

    return inf, start, end, num_bytes, use_bit, bpb, available_bytes,\
        data_mode, outf, extract


if __name__ == '__main__':

    # help
    if '-h' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, num_bytes, use_bit, bpb, available_bytes,\
        data_mode, outf, extract = set_params()

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        print('total available bytes for {} with bpb={}: {}'.format(
            inf, bpb, available_bytes
        ))
        exit()
    
    # create base generator and add additional ones
    base = BaseGenerator(num_bytes, extract)
    if not inf is None:    
        base.add_generator(WAVGenerator(inf, start, end, use_bit, bpb))
    if '--grc' in sys.argv:
        base.add_generator(GRCGenerator(num_bytes))
    if '--secrets' in sys.argv:
        base.add_generator(SecretsGenerator(num_bytes))

    # generate
    base.generate()

    # print or write to file
    base.display(data_mode, outf)


