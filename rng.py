'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen
from my_exception import MyException
from generator import BaseGenerator, SecretsGenerator, GRCGenerator, \
    WAVGenerator, WAVExtractGenerator, EvenGenerator, OddGenerator, MixGenerator

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

    start = set_param_int(sys.argv, '-s', 0)
    end = set_param_int(sys.argv, '-e', None)


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
    outf = set_param_gen(sys.argv, '--out', None)

    return inf, start, end, data_mode, outf


if __name__ == '__main__':

    # help
    if '-h' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, data_mode, outf = set_params()

    # add the WAV EvenGenerator
    m = MixGenerator(inf, start, end)

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        available_bytes = m.query()
        print('available bytes for {}: {}'.format(
            inf, available_bytes))
        exit()

    # generate
    m.generate()
    
    # create base generator and add additional ones
    base = BaseGenerator()

    num_bytes = len(m.data)
    base.add_generator(m)

    if '--grc' in sys.argv:
        base.add_generator(GRCGenerator(num_bytes))
    if '--secrets' in sys.argv:
        base.add_generator(SecretsGenerator(num_bytes))

    # generate
    base.generate()

    # print or write to file
    base.display(data_mode, outf)


