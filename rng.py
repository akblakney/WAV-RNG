'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen
from my_exception import MyException
from generator import BaseGenerator, SecretsGenerator, GRCGenerator, \
    WAVGenerator, WAVExtractGenerator, EvenGenerator, OddGenerator

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
    combine = set_param_int(sys.argv, '--combine', 1)
    header_len = 100
    post_extract = False
    wav_gen_mode = 'even'

    # extraction
    if '--post-extract' in sys.argv:
        post_extract = True

    # wav-mode
    if '--only-extract' in sys.argv:
        wav_gen_mode = 'extract'
    elif '--odd' in sys.argv:
        wav_gen_mode = 'odd'

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

    return inf, start, end, combine, \
        data_mode, outf, post_extract


if __name__ == '__main__':

    # help
    if '-h' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, combine, \
        data_mode, outf, post_extract = set_params()

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        filesize = os.path.getsize(inf)
        available_bytes = EvenGenerator.query(filesize, combine)
        ext_status = 'no post-extraction'
        if post_extract:
            ext_status = 'post-extraction'
            available_bytes //= 2

        print('available bytes with combining factor of {} and {}: {}'.format(
            combine, ext_status, available_bytes))
        
        exit()
    
    # create base generator and add additional ones
    base = BaseGenerator(None, post_extract)

    # add the WAV EvenGenerator
    e = EvenGenerator(inf, start, end, combine)
    num_bytes = e.num_bytes
    base.add_generator(e)

    if '--grc' in sys.argv:
        base.add_generator(GRCGenerator(num_bytes))
    if '--secrets' in sys.argv:
        base.add_generator(SecretsGenerator(num_bytes))

    # generate
    base.generate()

    # print or write to file
    base.display(data_mode, outf)


