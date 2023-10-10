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

import argparse
import numpy as np
from struct import pack, unpack
from Toolbox.utils import bit, read_bit_range
from Formats.header import *
from Formats.SEGY import SEGY_mandatory
from datetime import datetime as dt
import argparse


month_ind = {"JAN":1, "jan":1, "Jan":1, "1":0, "0":"Jan",
             "FEB":2, "feb":2, "Feb":2, "2":31, "31":"Feb",
             "MAR":3, "mar":3, "Mar":3, "3":59, "59":"Mar",
             "APR":4, "apr":4, "Apr":4, "4":90, "90":"Apr",
             "MAY":5, "may":5, "May":5, "5":120, "120":"May",
             "JUN":6, "jun":6, "Jun":6, "6":151, "151":"Jun",
             "JUL":7, "jul":7, "Jul":7, "7":181, "181":"Jul",
             "AUG":8, "aug":8, "Aug":8, "8":212, "212":"Aug",
             "SEP":9, "sep":9, "Sep":9, "9":243, "243":"Sep",
             "OCT":10, "oct":10, "Oct":10, "10":273, "273":"Oct",
             "NOV":11, "nov":11, "Nov":11, "11":304, "304":"Nov",
             "DEC":12, "dec":12, "Dec":12, "12":334, "334":"Dec"}

symbolic_commands = { 
    'a' : '+',
    's' : '-',
    'm' : '*',
    't' : '/'}

def parse_bit_command(command, data):
    ' will parse & evaluate symbolic parse command'
    # INFO:
    # This function takes a symbolic command and parses it for arithmetic
    # bit manipulation. Resolves for an integer only!
    # Commands:
    #           'x_' - defines bit command format
    #           'i'  - defines test situation, if...then ('e')
    #           'd'  - bit position -> 'o' = that position only, '+' that
    #                                   position up to bit index after '+'
    #                                   number = 0 up to defined bit index
    #           'c'  - additional arithmetic command, see symbolic_commands
    # 
    # Input : command, byte
    #
    # Output : returns integer value
    #
    # added: 18/2/16 by Ralf Hansen
    
    bit_string = ''
    actions = command.split('_')[1::]
    if len(actions) == 1:
        if actions[0][0] == 'r':
            bit_limits =  actions[0][1::].split('d')[1::]
            for byte in range(len(bit_limits)):
                if bit_limits[byte][0] == 'o':
                    bit_limits[byte] = bit_limits[byte][1::]
                    if '+' in bit_limits[byte]:
                        lims = bit_limits[byte].split('+')
                        bit_string = (bit_string + read_bit_range(
                                      data[byte], int(lims[0]), int(lims[1])
                                                                  ))
                    else:
                        bit_string = (bit_string + str(bit(
                                      data[byte],int(bit_limits[byte][0]))
                                                   ))
                else:
                    bit_string = (bit_string + read_bit_range(
                                      data[byte], 0, int(bit_limits[byte][0])
                                                              ))
            return_value = int(bit_string, 2)
            if len(bit_limits[-1]) > 2:
                add_command = bit_limits[-1][1::].split('c')[1::]
                for c in range(len(add_command)):
                     c_in = add_command[c][0]
                     c_val = add_command[c][1::]
                     return_value = eval(str(return_value)
                                         + symbolic_commands[c_in] 
                                         + c_val) 

    elif len(actions) > 1:
        passed = False
        for act in range(len(actions)):
            tests = actions[act][2::].split('e')
            if bit(data, int(tests[0][0])) == (int(tests[0][2::])):
                if act == 0:
                    return_value = int(tests[1])
                else:
                    if tests[1][0] == 'r':
                        bit_limits =  tests[1][1::].split('d')[1::]
                        for byte in range(len(bit_limits)):
                            if bit_limits[byte][0] == 'o':
                                bit_limits[byte] = bit_limits[byte][1::]
                                if '+' in bit_limits[byte]:
                                    lims = bit_limits[byte].split('+')
                                    bit_string = (bit_string 
                                                  + read_bit_range(
                                       data[byte], int(lims[0]), int(lims[1])
                                                                   )
                                                  )
                                else:
                                    bit_string = (bit_string + str(bit(
                                       data[byte], int(bit_limits[byte][0]))
                                                                       )
                                                  )
                            else:
                                bit_string = (bit_string + read_bit_range(
                                      data[byte], 0, int(bit_limits[byte][0])
                                                                          )
                                              )
                        return_value = int(bit_string, 2)
                        if len(bit_limits[-1]) > 2:
                            add_command = bit_limits[-1][1::].split('c')[1::]
                            for c in range(len(add_command)):
                                c_in = add_command[c][0]
                                c_val = add_command[c][1::]
                                return_value = eval(str(return_value)
                                             + symbolic_commands[c_in] 
                                             + c_val)
            
    return return_value

def hdr2bin(trace_hdrs, header_format_file, file_format):
    allhdrs = None
    for field in header_format_file:
        length, start, name, binary_format = field
        # verify existing values and substitute, or =0
        if name in trace_hdrs:
            val = trace_hdrs[trace_hdrs.index(name)+1]
        elif (file_format == 'sgy') and (name in SEGY_mandatory):
            val = SEGY_mandatory[name]
        else:
            val = 0
        # pack values as binary header string
        if length > 4:
            allhdr = pack('%s' % binary_format , 0)
            for i in range((length)-1):
                allhdr += pack('%s' % binary_format, 0)
            hdr = allhdr
        else:
            hdr = pack('%s' % binary_format, val)

        if allhdrs == None:
            allhdrs = hdr
        else:
            allhdrs += hdr
    return allhdrs      

def write_binary(trace_header, data, data_format, outfile):
    f = open(outfile, 'wb')

    if data_format == 'sg2':
        file_header = make_SEG2_file_header(trace_header)
        trace_start_pointer = len(file_header)
        f.write(file_header)
        for item in range(len(data)):
            tmp_trace_header = make_SEG2_trace_header(trace_header[item])
            f.write(tmp_trace_header)
            f.write(data[item])
            f.seek(item*4 + 32)
            f.write(pack('i', trace_start_pointer))
            trace_start_pointer += len(tmp_trace_header) + len(data[item])*4
            f.seek(trace_start_pointer)

    elif data_format == 'su':
        for item in range(len(data)):
            f.write(hdr2bin(trace_header[item],
                            SU_trace_header_format, data_format))
            f.write(data[item])

    elif data_format == 'sgy':
        f.write(hdr2bin(trace_header[0], 
                        SEGY_binary_file_header_format, data_format))
        for item in range(len(data)):
            f.write(hdr2bin(trace_header[item],
                            SU_trace_header_format, data_format))
            f.write(data[item])
            
    elif data_format == 'dat':
        for item in range(len(data)):
            f.write(" ".join(data[item].astype('str'))+'\r\n')

    f.close()

def get_header(headers, field):
    'returns value for header field'
    content = []
    for trace_items in headers:
        if field in trace_items:
            content += [trace_items[trace_items.index(field)+1]]
    return np.array(content)

def set_header(headers, field, values):
    '''changes header field(s). Set field name and value(s). Array of 
    values must = number of traces. Integer value is applied to all
    traces. An array of two values is interpreted as ['tracl','value']''' 

    # test if value is integer
    if isinstance(values, int):
        values = np.ones(len(headers))*values 
    else:
        values = map(int, values)
    if len(values) == len(headers):
        for trace in range(len(headers)):
            if field in headers[trace]:
                headers[trace][
                    headers[trace].index(field) + 1
                              ] = values[trace]
    elif len (values) == 2:
        for trace in range(len(headers)):
            if (headers[trace][
                    headers[trace].index('tracl') + 1
                              ] == values[0]):
                headers[trace][
                    headers[trace].index(field) + 1
                              ] = values[1]

def set_zero(headers, stream, traces):
    'zeros specified trace(s) data.'
    if isinstance(traces, int):
        traces = [traces]
    else:
        traces = map(int, traces)
    for n in range(len(headers)):
        if (headers[n][headers[n].index('tracl')+1] in traces):
            print headers[n][headers[n].index('tracl')+1]
            stream[n] = stream[n]*0

def parse_arguments():
    'parses input arguments'
    parser = argparse.ArgumentParser(
                          description='Binary file conversion.'
                          + ' Automatic source file format detection.',
                          conflict_handler='resolve')
    parser.add_argument('-v','--version', help='Current version', 
             action='version', version='%(prog)s ' + current_version)
    parser.add_argument('-infile', help='Input file name', 
             type=argparse.FileType('rb'),  default=sys.stdin, required=True)
    parser.add_argument('-outfile', help='Output file name', 
             type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-fileformat', choices=['sg2','sgy'],
             help='Output file format, seg2 or segy', required=True)
    parser.add_argument('-dataformat', default=4, choices=['1','2','4','5'], 
             help='Output file format: 1-Int16, 2-Int32, 4-float32 [default]'
                        + ', 5-float64')

    return parser.parse_args(sys.argv[1:])


def make_SEG2_trace_header(hdr):
    '''
    SEG2 trace header creation. See SEG2_trace_header_format for headers
    accessed.
    '''
    data_format = 4
    samples = hdr[hdr.index('ns')+1]
    data_block_size = samples * data_format
    trace_hdr_m = pack('2cH2ib','"','D', 484, data_block_size,
                       samples, data_format)
    for i in range(19):
        trace_hdr_m += pack('b',0)
    trace_hdr = ""
    tmp_header = pack('6c',"N","O","T","E"," ",'\n')
    for field in SEG2_trace_header_format:
        n, in_tr, in_m, seg2_h, h_val, scal, su_h = field
        # define main header fields
        if in_tr and in_m:
            if n == 1:
                val = hdr[hdr.index(su_h)+1]
                if scal > 1: 
                    val = float(val)/scal
                    zeroes = len(str(int(val))) + len(str(scal))
                    val = (str(val) + "000000")[0:zeroes]
                if seg2_h == 'DESCALING_FACTOR':
                    if val == 36 or val == 0: val = "4.270400E-005"
                    elif val == 24: val = "1.698500E-004"
                elif seg2_h == 'FIXED_GAIN':
                    if val == "0": val = "36"
                    val = str(val) + " DB"
            elif n > 1:
                su_h = su_h.split(" ")
                val = ""
                for i in range(n):
                    val += " " + str(hdr[hdr.index(su_h[i])+1])
            header_field = seg2_h + " " + str(val)
            trace_hdr += pack('H', len(header_field) + 3)
            for t in header_field:
                trace_hdr += pack('c', t)
            trace_hdr += pack('b',0)

        # define additional header fields
        elif in_tr and not in_m:
            val = hdr[hdr.index(su_h)+1]
            header_field = " " + seg2_h + " " + str(val) + " " + '\n'
            for t in header_field:
                tmp_header += pack('c', t)
            trace_hdr += pack('H', len(tmp_header)+5)
            trace_hdr += tmp_header
            trace_hdr += pack('c2b','\n',0,0)   

    trace_hdr_m += trace_hdr
    
    # identify size of header field, defaults to 484 (then mult. of 4 after)
    if len(trace_hdr_m) < 484:
        for i in range(484 - len(trace_hdr_m)):
            trace_hdr_m += pack('b', 0)
    else:
        for i in range(len(trace_hdr_m) % 4 + 4):
            trace_hdr_m += pack('b', 0)

    # return binary header
    return trace_hdr_m

def make_SEG2_file_header(hdr):
    'Creates SEG2 string header from header fields ns and dt'
    traces = len(hdr)
    samples = hdr[0][hdr[0].index('ns')+1]

    # define spacing
    if traces > 1:
        scale = hdr[0][hdr[0].index('scalco')+1]
        if scale == 0: scale = 1
        spacing = float( hdr[1][hdr[1].index('gx')+1] -
                         hdr[0][hdr[0].index('gx')+1]  )/scale
        lim = len(str(int(spacing)))+3
        if spacing == 0: 
            spacing = "1.00"
        else: 
            spacing = (str(spacing) + "000")[0:lim]
    else: 
        spacing = "1.00"

    # doing directly, not elegant, but gets the job done
    file_header = pack('2c','U',':') # 3a55 Hex
    file_header += pack('H', 1)
    file_header += pack('H', 4224)
    # 4224 bytes is based on 1064 bytes/traces
    file_header += pack('H',traces)
    file_header += pack('4b',0,0,0,1)
    file_header += pack('c','\n')
    file_header += pack('b',0)
    # writing 0's for trace block descriptors for now
    for n in range(18+4224):
        file_header += pack('b', 0)
    # set current date & time
    str(dt.now()).split()
    date = (str(dt.now()).split()[0]).split("-")
    if date[1][0] == '0': date[1] = date[1][1::]
    date = (date[2] + "/" 
           + month_ind[str(month_ind[str(date[1])])] 
           + "/" + date[0])
    time = (str(dt.now()).split()[1]).split(".")[0]
    file_header += pack('H',31)
    textual = "ACQUISITION_DATE " + str(date)
    for t in textual:
        file_header += pack('c',t)
    file_header += pack('b',0)
    file_header += pack('H',28)
    textual = "ACQUISITION_TIME " + str(time)
    for t in textual:
        file_header += pack('c',t)
    file_header += pack('b',0)

    # write file header fields
    tmp_header = pack('6c',"N","O","T","E"," ",'\n')
    for field in SEG2_trace_header_format:
         n, in_tr, in_m, seg2_h, h_val, scal, su_h = field
         if not in_tr and in_m:
             length = len(seg2_h) + len(h_val) + 4
             file_header += pack('H',length)
             textual = seg2_h + " " + h_val
             for t in textual:
                 file_header += pack('c',t)
             file_header += pack('b',0)
         elif not in_tr and not in_m:
            # set interval, if == 0
            if seg2_h == 'BASE_INTERVAL':
                h_val = spacing
            textual = " " + seg2_h + " " + h_val + " " + '\n'
            for t in textual:
                tmp_header += pack('c', t)

    file_header += pack('H', len(tmp_header)+5)
    file_header += tmp_header
    file_header += pack('c2b','\n',0,0)
    for zero in range(len(file_header) % 4 + 4):
        file_header += pack('b', 0)

    return file_header
