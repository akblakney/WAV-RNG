'''
This is the driver script which can be used to generate random numbers from
.wav files. For help run "python3 rng.py -h"

'''

import sys
import os
from params import set_param_int, set_param_gen
from my_exception import MyException
from generator import BaseGenerator, SecretsGenerator, GRCGenerator, \
    WAVGenerator, WAVExtractGenerator

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
    use_bit = None
    num_bytes = set_param_int(sys.argv, '--num_bytes', None)
    post_extract = False
    wav_gen_mode = 'regular'

    # extraction
    if '--post-extract' in sys.argv:
        post_extract = True

    # mode
    if '--only-extract' in sys.argv:
        wav_gen_mode = 'extract'
    elif '--even' in sys.argv:
        wav_gen_mode = 'even'
    elif '--odd' in sys.argv:
        wav_gen_mode = 'odd'
        
#    if post_extract and only_extract:
#        raise MyExcpetion('Cannot select both --only-extract and --post-extract options')

    if not inf is None:


        start = set_param_int(sys.argv, '-s', 0)
        end = set_param_int(sys.argv, '-e', None)

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

    # set output filename
    outf = set_param_gen(sys.argv, '--out', None)

    return inf, start, end, num_bytes, use_bit, bpb, \
        data_mode, outf, post_extract, wav_gen_mode


if __name__ == '__main__':

    # help
    if '-h' in sys.argv:
        my_help()
        exit()

    # set params
    inf, start, end, num_bytes, use_bit, bpb, \
        data_mode, outf, post_extract, wav_gen_mode = set_params()

    # query for how many bytes can be generated
    if '-q' in sys.argv:
        filesize = os.path.getsize(inf)
        available_bytes = None
        if wav_gen_mode == 'regular':
            available_bytes = WAVGenerator.query(filesize, bpb)
        elif wav_gen_mode == 'extract':
            available_bytes = WAVExtractGenerator.query(filesize)
        elif wav_gen_mode == 'even':
            available_bytes = WAVEvenGenerator.query(filesize)
        elif wav_gen_mode == 'odd':
            available_bytes = WAVOddGenerator.query(filesize)

        print('available bytes: {}'.format(available_bytes))
        
        exit()
    
    # create base generator and add additional ones
    base = BaseGenerator(num_bytes, post_extract)

    # add only one type of WAV generator depending on only/no extraction
    if not inf is None:    
        if only_extract:
            base.add_generator(WAVExtractGenerator(inf, start, end))
        else:
            base.add_generator(WAVGenerator(inf, start, end, use_bit, bpb))
    if '--grc' in sys.argv:
        base.add_generator(GRCGenerator(num_bytes))
    if '--secrets' in sys.argv:
        base.add_generator(SecretsGenerator(num_bytes))

    # generate
    base.generate()

    # print or write to file
    base.display(data_mode, outf)


