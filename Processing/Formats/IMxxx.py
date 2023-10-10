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

from Formats.header import *
import numpy as np
from struct import pack, unpack
from Toolbox.utils import bit, read_bit_range
from Formats.tools import *

header_ascii = {
    # Format : [data bytes (8 bit), header bytes,  zero fill]
    'IPX': [0, 112, 15],
    'IMX': [252, 112, 19],
    'IGX': [500, 112, 27] };

class Imagenix:
    'Class to parse binary file format data from Imagenix'
    def __init__(self, binary_file):
        self.binary_file = binary_file
        self.fileformat = 'su'
        self.pos = 0
        self.band = 0
        self.tracl = 0
        self.stream = []
        self.trace_hdrs = []
        self.text = []
        # open file
        with open(binary_file,'rb') as f: 
            self.bin = f.read()
        # set Imagenix binary file format
        self._binff = "".join(unpack('3c', self.bin[0:3])).lower()
        # assign zero headers for SU trace headers
        for field in SU_trace_header_format:
            setattr(self,field[2], 0)
        # assign zero headers for reading Imaginex binaries
        for field in eval('Im' + self._binff + '_trace_header_format'):
            setattr(self,field[2], None) 
        self.read()     

    def parse_trace_hdrs(self):
        'parse trace header information'
        for field in eval('Im' + self._binff + '_trace_header_format'):
            # define variables based on input header field
            length, start, name, bin_format = field
            start = int(start) + self.pos
            if bin_format == 'c':
                setattr(
                   self, name, "".join(unpack('%s%s' % (length, bin_format),
                   self.bin[start:(start+int(length))]))
                       )
            elif bin_format == 'b':
                setattr(
                   self, name, unpack('%s%s' % (length, bin_format), 
                   self.bin[start:(start+int(length))])[0]
                       )
            elif bin_format[0] == 'x':
                value = parse_bit_command(bin_format, 
                                         self.bin[start:(start+int(length))])
                setattr(self, name, value)

    def trace_data(self):
        'parse data stream'
        # calculate header information
        self.parse_trace_hdrs()
        # define byte window
        startbyte = self.pos + header_ascii[self.read_ascii_header][1]
        endbyte = startbyte + (self.band)
        # unpack data
        data = np.array(unpack('%ib' % (endbyte - startbyte), 
                        self.bin[startbyte:endbyte]))
        # assign ns
        self.ns = self.band
        # calculate dt in ms water velocity of 1450m/s or file specified
        if hasattr(self, 'water_velocity'):
            if self.water_velocity == 0:
                water_velocity = 1500
            else:
                water_velocity = self.water_velocity
        else:
            water_velocity = 1500
        self.dt = ( (float(self.range*2)/water_velocity) 
                    / float(self.ns)*10**6 )      
        return data

    def read(self):
        'reads header information and data for each trace into stream object'
        # define band width
        self.read_ascii_header = "".join(unpack('3c', self.bin[100:103]))
        self.band= header_ascii[self.read_ascii_header][0]

        # cycle through file 
        while self.pos < len(self.bin):
            # define headers and data
            self.stream += [self.trace_data()]
            # increment trace header
            self.tracl += 1
            # assign time
            self.hour, self.minute, self.second = map(
                                        int, self.time.split(':')
                                                     )
            # assign date
            day, month, self.year = str(self.date).split("-")
            self.year = int(self.year)
            self.day = (month_ind[str(month_ind[month])] + int(day))
            # capture text
            self.text += [self.header_text]                           
            # setting header list
            trace_hdr = []
            for field in SU_trace_header_format:
                length, start, name, binary_format = field
                val = eval('self.' + name)
                trace_hdr += [name, val]
            self.trace_hdrs += [trace_hdr]
            # shift byte window
            self.pos += (header_ascii[self.read_ascii_header][1] + self.band  
                         +  header_ascii[self.read_ascii_header][2] + 1)
            
        self.stream = np.array(self.stream, dtype='float32')

    # test for defined format string
    if 'args.fileformat' in globals():
        self.setformat(args.fileformat)

    def write(self, outfile):
        'writes to file, format : su, seg2 or sgy'
        write_binary(self.trace_hdrs, self.stream, self.fileformat, outfile)

    def header(self, field):
        'returns value for header field'
        return get_header(self.trace_hdrs, field)

    def setheader(self, field, values):
        '''changes header field(s). Set field name and value(s). Array of 
        values must = number of traces. Integer value is applied to all
        traces. An array of two values is interpreted as ['tracl','value']''' 
        set_header(self.trace_hdrs, field, values)

    def zero(self, traces):
        'zeros specified trace data.'
        set_zero(self.trace_hdrs, self.stream, traces)

