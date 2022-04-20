from urllib.request import urlopen
from bs4 import BeautifulSoup

class MyException(Exception):
    pass

# gets 64 random hex characters from grc.com/passwords.htm
def hex_from_grc():
    url = 'https://www.grc.com/passwords.htm'
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features='html.parser')
    text = soup.get_text()

    # find hex location
    search = '64 random hexadecimal characters (0-9 and A-F):'
    if not search in text:
        raise MyException('Error: search key not found on grc website')
    index = text.index(search) + len(search)
    
    ret = text[index:index+64]

    # make sure it is actually hex
    try:
        int(ret, 16)
    except ValueError:
        raise MyException('Retreived string from grc is not hexadecimal')

    return ret

