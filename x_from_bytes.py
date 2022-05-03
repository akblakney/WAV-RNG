'''
This file contains methods that bytes to/from various different formats,
such as hexadecimal digits, ascii, decimal, etc.
'''

# get hex from single byte
def hex_from_byte(b):
    return hex(b)[2:].rjust(2,'0')

# get hex from bytearray
def hex_from_bytes(b):
    ret = ''
    for x in b:
        ret = ret + hex(x)[2:].rjust(2,'0')
    return ret

# get binary from single byte
def binary_from_byte(b):
    return bin(b)[2:].rjust(8,'0')

# get binary from bytearray
def binary_from_bytes(b):
    ret = ''
    for x in b:
        curr = bin(x)[2:].rjust(8,'0')
        ret = ret + curr
    return ret

# get digit from single byte
def digit_from_byte(x):
    if x > 199:
        return None
    # single digit
    if x < 10:
        return '0{}'.format(x)
    # two digits
    elif x < 100:
        return str(x)
    # three digits
    elif x >= 100:
        return str(x)[1:]
    else:
        assert(False)
    

# b is a byte array, generate digits accordingly
def digits_from_bytes(b):
    ret = ''
    for x in b:
        curr = digit_from_byte(x)
        if curr is not None:
            ret = '{}{}'.format(ret, digit_from_byte(x))

    return ret

# get ascii from bytearray
def ascii_from_bytes(b):
    ret = ''
    byte_to_ascii = {
        0 : '0',
        1 : '1',
        2 : '2',
        3 : '3',
        4 : '4',
        5 : '5',
        6 : '6',
        7 : '7',
        8 : '8',
        9 : '9',
        10 : 'a',
        11 : 'b',
        12 : 'c',
        13 : 'd',
        14 : 'e',
        15 : 'f',
        16 : 'g',
        17 : 'h',
        18 : 'i',
        19 : 'j',
        20 : 'k',
        21 : 'l',
        22 : 'm',
        23 : 'n',
        24 : 'o',
        25 : 'p',
        26 : 'q',
        27 : 'r',
        28 : 's',
        29 : 't',
        30 : 'u',
        31 : 'v',
        32 : 'w',
        33 : 'x',
        34 : 'y',
        35 : 'z',
        36 : '!',
        37 : '@',
        38 : '#',
        39 : '$',
        40 : '%',
        41 : '^',
        42 : '&',
        43 : '*',
        44 : '(',
        45 : ')',
        46 : '-',
        47 : '_',
        48 : '=',
        49 : '+',
        50 : '[',
        51 : '{',
        52 : ']',
        53 : '}',
        54 : ';',
        55 : ':',
        56 : '\'',
        57 : '\"',
        58 : '|',
        59 : ',',
        60 : '<',
        61 : '.',
        62 : '>',
        63 : '/',
        64 : '?',
        65 : '~',
        66 : 'A',
        67 : 'B',
        68 : 'C',
        69 : 'D',
        70 : 'E',
        71 : 'F',
        72 : 'G',
        73 : 'H',
        74 : 'I',
        75 : 'J',
        76 : 'K',
        77 : 'L',
        78 : 'M',
        79 : 'N',
        80 : 'O',
        81 : 'P',
        82 : 'Q',
        83 : 'R',
        84 : 'S',
        85 : 'T',
        86 : 'U',
        87 : 'V',
        88 : 'W',
        89 : 'X',
        90 : 'Y',
        91 : 'Z'
    }
    for x in b:
        if x >= 184:
            continue
        if x > 91:
            x -= 92
        curr = byte_to_ascii[x]
        ret = '{}{}'.format(ret, curr)
    return ret


