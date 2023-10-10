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
                  
class SEG2:
    'Class to parse binary SEG2 format data from Geometrics, Use .read()'
    def __init__(self, binary_file):
        self.fileformat = 'su'
        self.band = 0
        self.tracl = 0
        self.trace_hdrs = []
        self.hdr = None
        self.stream = []
        # open file
        f = open(binary_file,'rb') 
        self.bin = f.read()
        f.close()
        # assign zero headers for SU trace headers
        for field in SU_trace_header_format:
            setattr(self,field[2], 0)
        # assign SEG2 header fields
        for field in SEG2_trace_header_format:
            setattr(self,field[3], field[4])
        # assign file variables
        self.traces = unpack('H',self.bin[6:8])[0]
        # read data
        self.read()
        
    def read_file_header(self, hdr_pointer):
        in_header = True
        while in_header:
            length = unpack('H',self.bin[hdr_pointer:hdr_pointer+2])[0]
            if length > 0:
                string = "".join(unpack('%sc' % str(length-3),
                         self.bin[
                         hdr_pointer+2:hdr_pointer+length-1
                                 ])).split(" ")
                # seperate "NOTE:" section into variables
                if "\n" in string:
                    string = " ".join(string).split(" \n")
                    for i in range(len(string)):
                         if " " in string[i]:
                             variable = string[i].split()
                             setattr(self,variable[0], 
                                 " ".join(variable[1:len(variable)+1]))

                else:
                    setattr(self,string[0], 
                                  " ".join(string[1:len(string)+1]))
                hdr_pointer += length

            else:
                in_header = False

    def assign_header_values(self,target_format):
         'assigns header values from/to su/seg2'
         if target_format == 'su':
              for field in SEG2_trace_header_format:
                 n, in_tr, in_m, seg2_h, h_val, scal, su_h = field
                 val = eval('self.' + seg2_h)
                 if (val == 'NONE') or (scal == 0):
                     val = '0'
                 val = val.split(" ")
                 if n == 1:
                     setattr(self, su_h, int(float(val[0])*scal))
                 if n > 1:
                     su_h = su_h.split(" ")        
                     for ind in range(n):                        
                         setattr(self, su_h[ind], int(float(val[ind])*scal))

    def read(self):
        'parse header info and trace data into header and stream objects'

        # read main file headers such as date & time'
        self.read_file_header(unpack('H',self.bin[4:6])[0]+32)
        self.if_read = True

        # parse trace header information'
        for i in range(self.traces):
            trace_index=unpack('i',self.bin[
                       32+i*4:32+i*4+4])[0]
            # Reading Trace...
            # defining length of header variables
            string_header_block = unpack(
                         'H',self.bin[(trace_index+2):(trace_index+4)])[0]
            Trace_pointer = trace_index + 32

            # parse header variables and write to list
            self.read_file_header(Trace_pointer)
            
            # defining data block length 
            data_block = unpack(
                      'i',self.bin[(trace_index+4):(trace_index+8)]
                               )[0] 
            data_block_start = trace_index + string_header_block
            data_block_end = data_block_start + data_block

            # defining data type & length
            data_type = unpack(
                       'b',self.bin[(trace_index+12):(trace_index+13)]
                               )[0]
            if data_type == 1 :
                length = 2
                data_char = 'H'
            elif data_type == 2 :
                length = 4
                data_char = 'I'
            elif data_type == 3 :
                print("20 bit SEG-D data format not supported")
                break
            elif data_type == 4 :
                length = 4
                data_char = 'f'
            elif data_type == 5 :
                length = 8
                data_char = 'd'

            data_pointer = data_block_start
            data=[]
            # parse data variables
            while data_pointer < data_block_end:
                sample=unpack('%s' % data_char,
                     self.bin[data_pointer:data_pointer + length]
                             )[0]
                data_pointer+=length
                data+=[sample]

            data=np.array(data, dtype='float32')
            self.stream += [data]

            # assign ns
            self.ns = unpack(
                      'i',self.bin[(trace_index+8):(trace_index+12)]
                               )[0]
            # assign scale for locations
            self.scalco = 100

            # assign Date/Time
            date = self.ACQUISITION_DATE.split("/")
            self.day = month_ind[str(month_ind[date[1]])]+ int(date[0])
            self.year = int(date[2])
            time = self.ACQUISITION_TIME.split(":")
            self.hour = int(time[0])
            self.minute = int(time[1])
            self.second = int(time[2])

            # assign data_type
            self.data_format = unpack(
                      'b',self.bin[(trace_index+12):(trace_index+13)]
                               )[0]

            # assign header values 
            self.assign_header_values('su')

            # make list and binary headers
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

