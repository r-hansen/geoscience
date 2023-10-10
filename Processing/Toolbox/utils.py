#!/bin/python env
"""
Copyright (c) 2016 by Ralf Hansen @ Frontier Geosciences Inc.
North Vancouver, B.C., Canada.
All Rights Reserved

This program is free software. You can redistribute it and/or modify this
software and its documentation for any purpose and without fee, provided that
the above copyright notice appear in all copies and that both that copyright
notice and this permission notice appear in supporting documentation, and 
that the name of the original authors not be used in advertising or publicity
pertaining to distribution of the software without specific, written prior
permission.
_____________________________________________________________________________

DISCLAIMER : This program is distributed in the hope that it will be useful,
             but WITHOUT ANY WARRANTY; without even the implied warranty of
             MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT
             SHALL AUTHOR OR ASSOCIATES BE LIABLE FOR ANY SPECIAL, INDIRECT
             OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
             FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
             CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF 
             OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
_____________________________________________________________________________

See Readme for detailed information

"""

import sys, os
import numpy as np
from struct import pack, unpack

utils_version = "0.0.2"

def bit(byte,index):
    'returns numbered bit value 0 or 1 for indexed bit in a byte'
    # INFO:
    # This function takes returns a bit value 0 or 1 in a specific index
    # position as defined by the user. sys.byteorder defines high or low
    # bit first
    #
    # Input : byte, bit index (0 to 7)
    #
    # Output : returns bit value
    #
    # added: 18/2/16 by Ralf Hansen
        
    i, j = divmod(index, 8)

    # Uncomment this if you want the high-order bit first
    # j = 8 - j

    if ord(byte[i]) & (1 << j):
            return 1
    else:
            return 0

def read_bit_range(byte, start, end):
    'returns bit string for bits range (incl. of end index) of a byte'

    # INFO:
    # This function takes returns a bit value 0 or 1 in a specific index
    # position as defined by the user. sys.byteorder defines high or low
    # bit first
    #
    # Input : byte, start bit index, end bit index
    #
    # Output : returns bit string
    #
    # added: 18/2/16 by Ralf Hansen
    bit_string =''
    for i in range(end-start+1):
        bit_string = str(bit(byte, i+start)) + bit_string
    return bit_string

class fdtect:
    '''File assessment; gives file size, reads binary data, tests formats
       Assign i.e. y=fff(*). Call y.testAll() or test4*format*
       Accessible:
                 y.filesize (bytes)
                 y.bin (binary data of file)
                 after y.test*(): y.valid (True/False)
                                  y.fileformat (i.e. 'su')
       Tested file formats: Seismic Unix SU
                         SEG-Y
                         Geometrics SEG-2 
                         GSSI DZT
                         Imagenix (81e, 851, 852)
    ''' 
    # INFO:
    # This class does a rudimentary check on a file for known designators
    # and identifies the appropriate format. Please NOTE that by the 
    # inherent limitations of the crude test scenario, a check may
    # pass a test irrespective of actual format.
    # Currently can verify SEG2, SEGY, SU, DZT, Im88b, Im851 formats
    # Call testAll(INFILE) or specific i.e. test4SU(INFILE)
    #
    # Input : INFILE
    #
    # Output : returns True/False, Format ('su','sgy' etc...)
    #
    # added: 18/2/16 by Ralf Hansen
    
    def __init__(self, binary_file):
        self.binary_file = binary_file
        self.fileformat = 'none'
        self.valid = False
        self.filesize = os.stat(binary_file).st_size
        with open(binary_file,'r') as f:
            self.bin = f.read(5000)
        self.filesize = os.stat(binary_file).st_size

    def testAll(self):
        ext = self.binary_file.split('.')[-1]
        if not self.valid:
            self.test4SGY()
        if not self.valid:
            self.test4SU()
        elif self.valid and (ext == 'su'):
            self.test4SU()
        if not self.valid:
            self.test4SEG2()
        elif self.valid and (ext == 'sg2' or ext == 'dat'):
            self.test4SEG2()
        if not self.valid:
            self.test4DZT()
        elif self.valid and (ext == 'dzt'):
            self.test4DZT()
        if not self.valid:
            self.test4Im()
        elif self.valid and (ext[0] == '8'):
            self.test4Im()

    def test4SGY(self):
        if self.filesize > 3840:
            div = unpack('H', self.bin[3219:3221])[0]*4 + 240
            if ( isinstance(div,int) and 
                 (self.filesize -3600) % div == 0 ):
                self.valid = True
                self.fileformat = 'sgy'

    def test4SU(self):
        if self.filesize > 240:
            div = unpack('H',self.bin[114:116])[0] *4 + 240
            if isinstance(div,int) and self.filesize % div == 0:
                self.valid = True
                self.fileformat = 'su'
        
    def test4SEG2(self):
        if self.filesize > 4220:
            if ( "".join(unpack('2c', self.bin[0:2])) == 'U:' or
                 "".join(unpack('2c', self.bin[0:2])) == ':U' ):
                self.valid = True
                self.fileformat = 'sg2'

    def test4DZT(self):
        if self.filesize > 1024:
            div = unpack('H', self.bin[4:6])[0]
            if div == 0 : div = 1
            if (isinstance(div,int) and 
                (self.filesize - 1024) % div == 0 ):
                self.valid = True
                self.fileformat = 'dzt'

    def test4Im(self):
        if self.filesize > 112:
            Im_id = "".join(unpack('3c',self.bin[0:3])).lower()
            if Im_id == '851' or Im_id == '81e' or Im_id == '852':
                self.valid = True
                self.fileformat = Im_id
                
                
def txt2array(infile, delim = ' '):
    'will convert input numeric ascii data file to numpy array, deliminator can be set'
    
    # INFO:
    # This function turns a ascii data file into a numpy floating point array
    # Automatically excludes all text, including scientific notation. 
    # Uses first line as collumn reference, and excludes all lines that do
    # not meet the numeric collumn total
    #
    # Input : INFILE, opt. delim = ' ' [DEFAULT]
    #
    # Output : returns array of dimension = # of entries and # of lines
    #
    # added: 14/3/16 by Ralf Hansen
    
    data = []
    with open(infile) as f:
        # Read file line by line
        setref = True
        for newline in f.readlines():
            cref = 0
            # assign to object stream 
            numeric = []
            tmp = newline.strip("\r").strip("\n").split(delim)
            for index in range(len(tmp)):
                if isnumeric(tmp[index]):
                    cref += 1
                    numeric += [tmp[index]]
            if setref:
                absref = cref
                setref = False

            if cref == absref:
                print absref
                data += [numeric]

    return np.array(data, dtype = 'float32')
    
def isnumeric(value):
    ' will take a string object and verifies if it is numeric'

    # INFO:
    # This function verifies if a string is numeric in value
    #
    # Input : VALUE
    #
    # Output : returns True or False
    #
    # added: 22/3/16 by Ralf Hansen
    
    vals = value.strip().split('.')
    case = True
    for val in vals:
        # remove scientific notation
        val = val.replace('e','').replace('+','').replace('-','')
        if not val.isdigit():
            case = False
    return case
    


