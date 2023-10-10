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

class DZT:
    'Class to parse binary .dzt format data from GSSI, Use .read()'
    'Binary file does not contain trace headers' 
    def __init__(self, binary_file):
        self.binary_file = binary_file
        self.fileformat = 'su'
        self._pos = 0
        self._band = 0
        self._tracl = 0
        self._trace_hdrs = []
        self.stream = []
        # open file
        with open(binary_file,'rb') as f: 
            self.bin = f.read()
        # assign zero headers for SU trace headers
        for field in SU_trace_header_format:
            setattr(self,field[2], 0)
        # assign zero headers for reading binaries
        for field in DZT_trace_header_format:
            setattr(self,field[2], 0)
        # read data
        self.read()

    def _parse_trace_hdrs(self):
        'parse trace header data'
        for field in DZT_trace_header_format:
            # define variables based on input headerfield
            length, start, name, bin_format = field
            if bin_format == 'c':
                setattr(self, name, "".join(
                                   unpack('%s%s' % (str(length), bin_format),
                                   self.bin[start:(start+length)])
                                            ))
            elif bin_format == 'x':
                setattr(self, name, self.bin[start:(start+length)])
            else:
                setattr(
                   self, name, unpack('%s' % (bin_format), 
                   self.bin[start:(start+length)])[0]
                       )

    def _trace_data(self):
        'parse data stream'
        # define byte window
        startbyte = self.data_offset + self._pos
        endbyte = startbyte + self._band
        # unpack data
        data = unpack('%iH' % self.ns, 
                   self.bin[startbyte:endbyte])
        data = np.array(data)
        self.dt = 1000*(self.range_ns / float(self.ns))
        return data

    def read(self):
        'reads header information and data for each trace into stream object'
        # calculate header information
        self._parse_trace_hdrs()
        # set date & time
        self.year = 1980 + int(read_bit_range(self.date_c[3],1,7),2)
        month = ( int((read_bit_range(self.date_c[3],0,0) + 
                       read_bit_range(self.date_c[2],5,7)),2) )
        self.day = int(read_bit_range(self.date_c[2],0,5),2)
        self.day = month_ind[str(month)] + int(self.day)
        self.hour = int(read_bit_range(self.date_c[1],3,7),2)
        self.minute = ( int((read_bit_range(self.date_c[1],0,2) + 
                        read_bit_range(self.date_c[0],5,7)),2) )
        self.second = int(read_bit_range(self.date_c[0],0,4),2)       
        # define data band        
        self._band = self.ns *(self.data_bits/8)
        self.gelev = self.range
        self.selev = self.dia_const
        while self._pos < (len(self.bin) - self._band):
            # assign trace data to trace object file
            self.stream += [self._trace_data()]
            # increment trace header
            self._tracl += 1
            # setting header list
            trace_hdr = []
            for field in SU_trace_header_format:
                length, start, name, binary_format = field
                val = eval('self.' + name)
                trace_hdr += [name, val]
            self._trace_hdrs += [trace_hdr]
            # shift byte window
            self._pos += self._band

        self.stream = np.array(self.stream, dtype='float32')

    # test for defined format string
    if 'args.fileformat' in globals():
        self.setformat(args.fileformat)

    def write(self, outfile):
        'writes to file, format : su, seg2 or sgy'
        write_binary(self._trace_hdrs, self.stream, self.fileformat, outfile)

    def header(self, field):
        'returns value for header field'
        return get_header(self._trace_hdrs, field)

    def setheader(self, field, values):
        '''changes header field(s). Set field name and value(s). Array of 
        values must = number of traces. Integer value is applied to all
        traces. An array of two values is interpreted as ['tracl','value']''' 
        set_header(self._trace_hdrs, field, values)

    def zero(self, traces):
        'zeros specified trace data.'
        set_zero(self._trace_hdrs, self.stream, traces)

