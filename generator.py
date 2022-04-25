'''
This file contains classes used to generate random numbers
'''

from abc import ABC, abstractmethod
from x_from_bytes import digits_from_bytes, ascii_from_bytes, binary_from_bytes,\
    hex_from_bytes
from my_exception import MyException
import secrets
from grc import hex_from_grc
import os

# abstract Generator class
# contains a generate method that generates random bytes
# other methods return those bytes in different formats
class Generator(ABC):

    # calls self.generate
    def __init__(self):
        self.generate()

    # return the generated raw bytes
    def get_bytes(self):
        return self.data
    
    # return generated bytes in ascii form
    def get_ascii(self):
        return ascii_from_bytes(self.data)

    # return generated bytes in digits form
    def get_digits(self):
        return digits_from_bytes(self.data)

    # return generated bytes in binary form
    def get_binary(self):
        return binary_from_bytes(self.data)

    # return generated bytes in hexadecimal form
    def get_hex(self):
        return hex_from_bytes(self.data)

    # abstract method
    # generate the random bytes and store in self.data
    # retrieve with get_x methods above
    @abstractmethod
    def generate(self):
        pass

# subclass of the Generator class which generates random bytes by
# pulling from the grc passwords (PRNG) website
class GRCGenerator(Generator):

    def __init__(self, num_bytes):
        if num_bytes > 32:
            raise MyException('Error: GRCGenerator can only generate 32 bytes')
        self.num_bytes = num_bytes
        super().__init__()

    def generate(self):
        h = hex_from_grc()[:2*self.num_bytes]
        b = bytes.fromhex(h)
        self.data = b

# subclass of Generator
# generates random bytes via the secrets module
class SecretsGenerator(Generator):
    
    def __init__(self, num_bytes):
        self.num_bytes = num_bytes
        super().__init__()

    def generate(self):
        self.data = secrets.token_bytes(self.num_bytes)

# subclass of Generator
# generates random bytes via .wav files (of atmospheric noise)
# inf is input wav filename
# start and end give start and end of available bytes to get
# use_bit gives which bit to use in 16-bit wav chunks. If none,
# then xor all 16 bits
# bpb gives bits per block. Default is 16, but can be larger multiple
# of 16.
class WAVGenerator(Generator):
    
    def __init__(self, inf, start=0, end=None, use_bit=None, bpb=16):##

        # set defaults
        self.HEADER_LEN = 100

        self.inf = inf
        self.filesize = os.path.getsize(self.inf)
        self.bpb = bpb
        self.available_bytes = (self.filesize - self.HEADER_LEN) // self.bpb
        self.start = start
        if end is None:
            self.end = self.available_bytes
        else:
            self.end = end
        self.use_bit = use_bit
        
        self.num_bytes = self.end - self.start

        # verify start and end
        if self.start < 0 or self.start >= self.available_bytes:
            raise MyException('Invalid start position for wav file')
        if self.end < 1 or self.end > self.available_bytes:
            raise MyException('Invalid end position for wav file')
        if self.start >= self.end:
            raise MyException('Wav start position must be less than wav end pos')

        # verify use_bit
        if not self.use_bit is None:
            if self.use_bit >= self.bpb:
                raise MyException('use_bit must be less than bits per block')

        super().__init__()

    def generate(self):
        ret = bytearray()

        # start_index and end_index idex the bytes on the WAV file,
        # NOT the bytes to be returned
        start_index = self.HEADER_LEN + self.start * self.bpb
        end_index   = self.HEADER_LEN +   self.end * self.bpb

        file = open(self.inf, 'rb')

        # skip bytes
        _ = file.read(start_index)
        index = start_index

        # each iter generates a byte
        for i in range(self.num_bytes):

            wav_bytes = file.read(self.bpb)
            new_byte = self.byte_from_wav_bytes(wav_bytes)
            ret.append(new_byte)
            index += self.bpb

        assert(index == end_index)
        assert(len(ret) == self.end - self.start)

        file.close()
        self.data = ret

    # returns one byte generated from wb
    # take in self.bpb wav bytes, output single generated byte
    def byte_from_wav_bytes(self, wb):
        assert len(wb) == self.bpb
        bitstring = ''

        # outer loop will run exactly 8 times, each time adding a bit
        for i in range(0, self.bpb, self.bpb // 8):
            curr_bits = ''

            # inner loop
            # each iter will process one byte of wav data
            # each iter will add 8 bits to curr_bits
            for j in range(self.bpb // 8):
                curr_bits = curr_bits + bin(wb[i+j])[2:].rjust(8,'0')

            # this is because bpb wav bits are needed to generate one randombit
            assert(len(curr_bits) == self.bpb)

            # no use_bit to use XOR Method
            if self.use_bit is None:
                temp_sum = 0
                next_bit = '0'
                for x in curr_bits:
                    if x == '1':
                        temp_sum += 1
                if temp_sum % 2 == 1:
                    next_bit = '1'

            # use only the use_bit
            else:
                next_bit = curr_bits[self.use_bit]
            
            bitstring = bitstring + next_bit

        # now we should have a completed byte
        assert(len(bitstring) == 8)
        return int(bitstring, 2)

# generates random bytes by xor-ing the generated bytes from one or more
# sub-generators in self.generators
# display() method prints/writes generated bytes
class BaseGenerator(Generator):

    # sets num_bytes
    # initializes self.generators
    def __init__(self, num_bytes):
        self.generators = []
        self.num_bytes = num_bytes


    # adds g to self.generators
    def add_generator(self, g):
        # not sure if we want this
#        if g.num_bytes != self.num_bytes:
#            raise MyException('Added generator must have equal num_bytes')
        self.generators.append(g)

    # removes all generators and clears self.data
    def reset(self):
        self.generators = []
        self.data = None

    # Generator.generate implementation
    # set self.data according to self.generators[i].generate xor
    def generate(self):

        assert(len(self.generators) > 0)

        ret = self.generators[0].get_bytes()
        for i in range(1,len(self.generators)):
            curr = self.generators[i].get_bytes()
            assert(len(curr) == len(ret))
            ret = bytes(a ^ b for (a, b) in zip(ret, curr))
        self.data = ret

    # writes or prints self.data in desired format
    def display(self, data_mode, outf):

        # get data to write
        write_mode = 'w'
        if data_mode is None:
            ret = self.get_bytes()
            write_mode = 'wb'
        elif data_mode == 'ascii':
            ret = self.get_ascii()
        elif data_mode == 'binary':
            ret = self.get_binary()
        elif data_mode == 'hex':
            ret = self.get_hex()
        elif data_mode == 'digits':
            ret = self.get_digits()

        # write or print
        if outf is None:
            print(ret)
        else:
            with open(outf, write_mode) as f:
                f.write(ret)        
    
