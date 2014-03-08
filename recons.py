#!/usr/bin/env python
# File name:    mygcc.py
# Date:         2014/03/04 14:07
# Author:       Sridhar V Iyer (sridhar.v.iyer@gmail.com)
# Description:  gcc wrapper to avoid recompilation by caching them. 
#               Current use case is only for local user and not to be shared.
# TODO:         Json db to be replaced by sqllite to enable make -jX calls.


import sys
import json
import os.path
import os
import hashlib
import shutil
from subprocess import call
import subprocess
import pdb

from functools import partial

mydict = {}

def expmd5(filename, params, cc):
    cmd = cc+" -MM "+params+" "+filename
    cmdl = cmd.split()
    mstdout = subprocess.Popen(cmdl, stdout=subprocess.PIPE).communicate()[0]
    files = mstdout.split()[1:]
    currmod = True
    chfiles= ""

    for file in files:
        is_mod = md5sum(file, params)
        if is_mod[0] == False:
            chfiles = chfiles+" "+file
        currmod = is_mod[0] and currmod

    if currmod == False:
        print "Compilation of "+filename+" needed because following files changed: "+chfiles
    return currmod
    
def md5sum(filename,params):
    global mydict
    time = os.path.getmtime(filename)
    mhash = "" 
    if filename in mydict.keys():
        (mtime,mhash) = mydict[filename]
        if mtime == time:
            return True,mhash
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    d.update(params)
    mydict[filename] = (time,d.hexdigest())
    if mhash == d.hexdigest():
        return True, mhash
    return False, d.hexdigest()

def main(argv=None):
    global mydict
    if argv==None:
        argv=sys.argv

    if os.path.isfile('my_dict.json'):
        f = open('my_dict.json')
        mydict = json.load(f)
        f.close()

    dir = '/tmp/'
    #pdb.set_trace()
    length = len(argv)-1;
    cc = argv[1]
    params = ' '.join(argv[2:-3])

    obj = argv[-1]
    objname = obj.split('/')[-1]
    file = argv[-3]


    if expmd5(file, params, cc) and os.path.isfile(dir+objname):
        shutil.copy(dir+objname, obj)
    else:
        #compile
        #pdb.set_trace()
        print "Compiling"
        call(argv[1:])
        shutil.copy(obj, dir+objname)

    f = open('my_dict.json','w')
    json.dump(mydict,f)



    #Write main logic here

if __name__=="__main__":
    sys.exit(main())
