'''
This file contains classes used to generate random numbers.

bytes_from_block() takes as input a bytearray, which should contain entropy
generated from some separate source, and returns a full-entropy bytearray (as
long as the input had sufficient entropy...). Other options can be specified too.

generate_from_wav() takes as input a filename which should point to a .wav file
with recorded atmospheric noise, or some other high entropy file. Options specify
whether or not to use a hash to increase the robustness of the randomness generated,
and various other parameters

'''

from hashlib import sha512, blake2b
import os

def process_raw(raw_in, out_size):
    raw_size = len(raw_in)

    # extract even and odd bytes from the block
    even_bytes = bytearray([raw_in[i] for i in range(0, raw_size, 2)])
    odd_bytes =  bytearray([raw_in[i] for i in range(1, raw_size, 2)])

    assert(len(even_bytes) == len(odd_bytes))
    assert(len(even_bytes) == raw_size // 2)

    # smush even_bytes and odd-bytes each down to out_size each
    num_folds = (len(even_bytes) // out_size)
    even_out = bytes(out_size)
    odd_out = bytes(out_size)

    for i in range(num_folds):
        even_out = bytes(a ^ b for (a, b) in zip(even_out,
            even_bytes[out_size * i: out_size * (i+1)]))
        odd_out = bytes(a ^ b for (a, b) in zip(odd_out,
            odd_bytes[out_size * i: out_size * (i+1)]))
        
    assert(len(even_out) == out_size)
    assert(len(odd_out) == len(even_out))

    # xor even and odd outs
    raw_out = bytes(a^b for (a, b) in zip(even_out, odd_out))
    
    assert(len(raw_out) == out_size)   # output for SHA-512

    return raw_out

def process_hash(hash_in, hash_obj, out_size=64):

    hash_obj.update(hash_in)
    ret = hash_obj.digest()

    assert(len(ret) == out_size)
    return ret

def bytes_from_block(wav_bytes, out_size=64, no_hash=False, hash_obj=None):

    n = len(wav_bytes)
    assert(n % (2 * out_size) == 0)

    # split into hash and raw portions
    hash_in = wav_bytes[: n // 2]
    raw_in = wav_bytes[n // 2 :]

    # raw portion
    raw_out = process_raw(raw_in, out_size)

    if no_hash:
        return raw_out
  
    # we are in hash portion, make sure we have existing hash_obj
    if hash_obj is None:
        raise BaseException('no hash object passed to method')

    # hash portion
    hash_out = process_hash(hash_in, hash_obj, out_size=out_size)

    # xor raw and hash portions
    ret = bytes(a ^ b for (a,b) in zip(raw_out, hash_out))

    assert(len(ret) == out_size)
    return ret

def query_blocks(filesize, block_size, header_len):
    return (filesize - header_len) // block_size

def generate_from_wav(inf, block_size=2048, start=0, end=None, header_len=100, 
    no_hash=False, hash_function='sha512', blake_key=b''):

    out_size = 64 # hardcode sha512 constant

    # verify block_size
    if block_size % (out_size * 2) != 0:
        raise BaseException('block size must be divisible by {}'.format(out_size*2))

    if header_len < 100:
        raise BaseException('header length must be at least 100')

    try:
        filesize = os.path.getsize(inf)
    except:
        raise BaseException('could not read file')

    # verify filesize with start and end
    total_blocks = query_blocks(filesize, block_size, header_len)
    if total_blocks < 1:
        raise BaseException('error: file size too small to generate a block')

    if end is None:
        end = total_blocks

    if start < 0 or start >= total_blocks:
        raise BaseException('start position out of bounds')
    if end <= 0 or end > total_blocks:
        raise BaseException('end position out of bounds')
    if start >= end:
        raise BaseException('start cannot be >= end')

    num_blocks = end - start

    # setup hash object applicable
    hash_obj = None
    if not no_hash:
        if hash_function == 'sha512':
            hash_obj = sha512()
        elif hash_function == 'blake2b':
            hash_obj = blake2b(key=blake_key)
        else:
            raise BaseException('invalid hash specified.')

    # begin parsing wav file
    f = open(inf, 'rb')
    ret = bytearray()

    # skip header
    _ = f.read(header_len + start * block_size)

    # main loop
    for _ in range(num_blocks):
        wav_bytes = f.read(block_size)
        assert(len(wav_bytes) == block_size)
        out_bytes = bytes_from_block(wav_bytes, out_size=out_size, \
            no_hash=no_hash, hash_obj=hash_obj)
        assert(len(out_bytes) == out_size)
        ret.extend(out_bytes)

    f.close()
    return ret


