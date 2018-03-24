#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, json, os, subprocess, base64, string, os.path
from itertools import cycle

if not (sys.version_info > (3, 0)):
    sys.stderr.write('Please use python3.\n')
    exit(1)

import secrets

def useKey(i, force = False):
    f = get_file()
    if not force:
        f['offset'] = max(i, f['offset'])
    else:
        f['offset'] = i
    open('keys.json', 'w').write(json.dumps(f))

def freeKey():
    f = get_file()
    offset = (f['offset'] + 1)
    maxoffset = len(f['keys'])
    if offset >= maxoffset:
        sys.stderr.write('Error: Time to generate new keys!')
        exit(1)
    else:
        return offset

def get_file():
    return json.loads(open('keys.json').read())

def get_key(offset = None):
    f = get_file()
    if offset is None:
        offset = (f['offset'] + 1)
    return base64.b64decode(f['keys'][offset])
    
def xor(s0, s1):
    if type(s0) is str:
        s0 = bytes(s0, 'utf-8')
    if type(s1) is str:
        s1 = bytes(s1, 'utf-8')
    l = [ a ^ b for (a,b) in zip(s0,cycle(s1)) ]
    s = ''
    for c in l:
        s += chr(c)
    return l

def decrypt(message, i = None):
    key = get_key()
    if not i is None:
        key = get_key(i)
    
    s = ''
    for c in xor(key, message):
        if c != 0:
            s += chr(c)
        else:
            return s
    
def encrypt(message, i = None):
    key = get_key()
    if not i is None:
        key = get_key(i)
    
    if len(message) > len(key):
        sys.stderr.write('Warning: Message too long, trimming...\n')
        message = message[:len(key)]
    
    message = bytes(message, 'utf-8')
    
    # padding
    if not len(message) is len(key):
        message += bytes('\0', 'utf-8')
        message += secrets.token_bytes(len(key) - len(message))
    
    return xor(key, message)

def gen_key(length = 65536):
    task = subprocess.Popen('head -c ' + str(int(length)) +  ' /dev/urandom | base64', shell=True, stdout=subprocess.PIPE)
    key = task.stdout.read()
    assert task.wait() == 0
    return base64.b64encode(key).decode('utf-8')

def args(*args):
    return (sys.argv[1] in args)

if len(sys.argv) is 1 or args('-h', '--help'):
    print('_'*51 + '\n| -h/--help      |  Displays this help menu       |\n| -d/--decrypt   |  Decrypts a message from stdin |\n| -e/--encrypt   |  Encrypts a message from stdin |\n| -g/--generate  |  Generates new OTP keys        |\n| -i/--index     |  Sets the index (see example)  |\n' + '‾'*51);
elif args('-e', '--encrypt'):
    if not os.path.isfile('keys.json'):
        sys.stderr.write('keys.json does not exist. Please run with option --generate to generate new keys.\n')
        exit(1)
    
    message = (sys.argv[2] if len(sys.argv) >= 3 else  None)
    if message is None:
        message = input()
    
    i = freeKey()
    print(str(i) + ':' + base64.b64encode(bytes(encrypt(message, i))).decode('utf-8'))
    useKey(i)
elif args('-d', '--decrypt'):
    if not os.path.isfile('keys.json'):
        sys.stderr.write('keys.json does not exist. Please run with option --generate to generate new keys.\n')
        exit(1)
    
    message = input()
    s = message.split(':')
    i = int(s[0])
    m = str(s[1])
    print(decrypt(base64.b64decode(m), i))
    useKey(i)
elif args('-g', '--generate'):
    confirm = 'y'
    if os.path.isfile('keys.json'):
        confirm = input('Generating new keys will wipe the old keys, are you sure you want to proceed (y/N)? ')
    
    if confirm == 'y':
        if os.path.isfile('keys.json'):
            print('Making a backup of keys.json...')
            os.system('cp keys.json .keys.json.backup')
    
        length = 8192
        number = 1024
        
        keys = list()
        
        print('Creating ' + str(number) + ' new ' + str(length) + '-byte keys...')
        for i in range(0, number):
            keys.append(gen_key(length))
        
        print('Writing to file...')
        array = dict()
        array['offset'] = 0
        array['keys'] = keys
        
        open('keys.json', 'w').write(json.dumps(array, indent=4))
elif args('-i', '--index'):
    if len(sys.argv) <= 2:
        print('Current key index: ' + str(int(freeKey() - 1)))
    else:
        useKey(int(sys.argv[2]), True)
        print('New key index: ' + str(int(freeKey() - 1)))
else:
    print('Unknown argument. Try: ' + sys.argv[0] + ' --help')
