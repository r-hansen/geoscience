#!/usr/bin/python
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
import numpy as np
from Formats.header import SICK_trace_header_format
from Toolbox.geometry import radians, polar2cartesian

class SICK510:
    'class for parsing SICK 510-20100 Laser ascii data & writing a xyz cloud'
    
    # INFO:
    # This class reads the SICK 510 ascii output data format file and returns
    # an xyz cloud based on angular information of the first line entry. The
    # orientation of the axis of rotation can be set in degrees, where 
    # horizontal = 0 and the Lidar swath is taken in the horizontal plane. 
    # Right up = 90, Left up = -90/270.
    #
    #              z
    #              90
    #              |  /
    #              | /
    #              |/) angle
    #   180 --------------- 0 x  rotation axis tilted by inclination angle
    #            (/|             from x towards z on y axis. Assume a rotated
    #            / |             coordinate axis x and z in xz plane, with y 
    #           /  |             unchanged. Project onto rotated system, then
    #             270            project back onto x and z
    #             -z
    #
    #
    # File headers and data read into numpy array, collumn one of the .header 
    # file assumed to be the axis angular rotation factor, that can be 
    # augmented if needed by manipulating .header[:,0]. Any additional header
    # information is ignored by the internal function calls. The header can 
    # be changed directly in the header.py file if need be. When using 
    # .get_xyz, an angle in degrees is expected.
    #
    # Input :   ascii input file, 
    #           opt: inclination = : axis orientation, [DEFAULT = 0]
    #           opt: delim = : file format deliminator [Default =',']
    #
    # Function calls:
    #       .read()
    #           will parse the ascii_file, parsing N elements using the
    #           file seperator = delim. 
    #           .header (header) = file lines[0:hdrlim]
    #           .stream (data) = file lines[hdrlim:data]
    #
    #       .get_xyz(offset = 0, rotation = 0, scale = 1, 
    #                                                  cmin = -5, cmax = 185)
    #           will convert the data values to corresponding cartesian xyz 
    #           coordinates based on the polar coordinate system set up by 
    #           the Lidar position and input variables.
    #               offset = offset is distance from center of rotation to 
    #               center of Lidar mirror
    #               rotation = is the angular offset from recorded starting 
    #                          zero position to coordinate system zero
    #               scale = scaling factor for radial distance
    #               flip = data flip if orientation in reverse of coordinate
    #                      system
    #               cmin = is the minimum angle extent (degrees) of the lidar 
    #                      swath [DEFAULT = -5]
    #               cmax = is the maximum angle extent (degrees) of the lidar 
    #                      swath [DEFAULT = 185]
    #           Output :
    #               array of [x,y,z, length] values for each line of the 
    #               .stream data array
    #
    # added: 11/3/16 by Ralf Hansen

    def __init__(self, ascii_file, inclination = 0, delim = ','):
        self.delim = delim
        self.file = ascii_file
        self.header = []
        self.stream =[]
        self._hdrlim = len(SICK_trace_header_format)

        # set orientation to within system limits
        while inclination < 0: inclination += 360
        while inclination > 360: inclination -= 360
        self.inclination = inclination
               
        for field in SICK_trace_header_format:
            setattr(self,field[1], 0)

    def read(self):
        start = False
        with open(self.file) as f:
            # Read file line by line
            for newline in f.readlines():
                # assign to object stream 
                line = np.array(newline.strip("\r\n").split(self.delim))
                # assign reference hdr & exclude multiples of angle increment
                if start and not ref_hdr == line[0] and float(line[0]) >9000:
                    self.header += [line[0:self._hdrlim]]
                    self.stream += [line[self._hdrlim:len(line)-1]]
                ref_hdr = line[0]
                start = True
        self.header = np.array(self.header, dtype='float32')
        self.stream = np.array(self.stream, dtype='float32')

    def get_xyz(self, offset = 0., rotation = 0., scale = 1, flip = False,
                cmin = -5, cmax = 185):
        '''
        determines cartesion coordinates.
            opt. :  offset is distance from center of rotation to center of 
                    mirror
            opt. :  rotation is the angle from recorded zero to coordinate 
                    zero 
            opt. :  scale factor for radial distance
            opt. :  flip = TRUE, flip the data orientation, left to right
                    becomes right to left to agree with coordinate system
            opt. :  cmin is the min angle extent (degrees) of the lidar swath
            opt. :  cmax is the max angle extent (degrees) of the lidar swath
        '''

        xyz = []

        # gamma is the rotational axis inclination angle from horizontal
        # assume a rotated coordinate system
        gamma = float(self.inclination)

        for swath in range(len(self.stream)):
            # define lidar angular sample increment
            inc = (cmax - cmin) / float(len(self.stream[swath]))
            # beta is the axis rotational angle
            beta = float(self.header[swath, 0]) + rotation
            # determine xyz position for each sample in swath
            for sample in range(len(self.stream[swath])):
                # alpha is the angle of the laser ping on xy-swath plane
                # starts at cmin to cmax
                alpha = float(cmin + sample*inc)

                # mirror angle based on data flip setting
                if flip:
                    alpha = (alpha - cmax) *-1.

                # determine alpha quadrant
                z, projyzswath = polar2cartesian(
                            alpha, float(self.stream[swath, sample])*scale
                                            )
                # determine beta quadrant
                x, y = polar2cartesian(beta, projyzswath)

                # test for offset and add
                if offset > 0:
                    # determine offset correction
                    xadd, yadd = polar2cartesian(beta, offset)
                    y = y + yadd
                    x = x + xadd
                    
                # project into gamma quadrant
                #x = xswath #*np.cos(radians(gamma)) 
                #z = zswath #*np.cos(radians(gamma))

                xyz += [[x, y, z, self.stream[swath, sample]]]

        return xyz
