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

class SU:
    def __init__(self, binary_file):
        self.fileformat = 'su'
        self.tracl = 0
        self.trace_hdrs = []
        self.hdr = None
        self.stream = []
        self.if_read = False
        self.traces = 1
        self.spacing = 0
        # open file
        f = open(binary_file,'rb') 
        self.bin = f.read()
        f.close()
        # assign zero headers for SU trace headers
        for field in SU_trace_header_format:
            setattr(self,field[2], 0)
        # read data
        self.read()

    def read(self):
        'parse header info and trace data into header and stream objects'
        trace_count = 0
        band = 0
        while trace_count < self.traces:
            trace_hdr = []

            # read trace headers'
            for field in SU_trace_header_format:

                # define variables based on input headerfield
                length, start, name, bin_format = field
                start += (band * trace_count)
                if length == 8:
                    setattr(self, name, unpack('q',
                            self.bin[start:(start+length)])[0])
                else:
                    setattr(self, name, unpack('%s' % bin_format,
                            self.bin[start:(start+length)])[0])

            if self.traces == 1:
                band = 4 *self.ns + 240
                self.traces = len(self.bin)/band
                self.spacing = self.gx

            # read data block
            data = []
            for n in range(self.ns):
                data_start = band * trace_count + 240 + n*4
                data += unpack('f', self.bin[data_start:data_start+4])
            data = np.array(data, dtype='float32')
            self.stream += [data]

            # increment trace_count
            trace_count+=1
            if trace_count == 2:
                self.spacing  = self.gx - self.spacing

            # setting header list
            trace_hdr = []
            for field in SU_trace_header_format:
                length, start, name, bin_format = field
                val = eval('self.' + name)
                trace_hdr += [name, val]
            self.trace_hdrs += [trace_hdr]

    # test for defined format string
    if 'args.fileformat' in globals():
        self.setformat(args.fileformat)

    def write(self,outfile):
        'writes to file, format : su, seg2 or sgy; IEEE 32 bit floats'
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

