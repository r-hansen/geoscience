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


Contains various arithmetic approaches regarding geometric data manipulation
See Readme for detailed information

"""

import numpy as np
from pyproj import Proj

geometry_version = "0.0.3"

def inc2deg(data, angle, cmin=None, cmax=None):
    'will verify the calibration angle, can add cmin=..,cmax= for user input'

    # INFO:
    # This function takes an arbitrary array of data and converts values
    # to degrees based in data min,max. Overall limits = 0,360, or these
    # limits can be set by user defined input cmin=, cmax=
    #
    # Input : data = array of floating point values
    #
    # Output : returns data array of degree values
    #
    # added: 29/7/15 by Ralf Hansen

    # search for user defined input parameters
    if cmin == None: 
        cmin = min(data)
    if cmax == None: 
        cmax = max(data)

    return ((data[:] - cmin)/(cmax - cmin)*angle)


def radians(angle):
    'converts degrees to radians'
    # INFO:
    # This function converts degrees to radians
    #
    # Input : angle in degrees
    #
    # Output : angle in radians
    #
    # added: 29/7/15 by Ralf Hansen


    return float(angle) * (np.pi/180)

def polar2cartesian(angle, hypo):
    'convert from polar to cartesian. returns the two axis component values'

    # INFO:
    # This function takes an angle and line length of a polar coordinate 
    # system and converts values to cartesian system. Interprets 0/360 as
    # horizontal, 270/90 as -vertical/+vertical. Returns vertical, 
    # and horizontal component. Sets degrees based on data min, max 
    # limits = 0,360, or these limits can be set by user defined input 
    # cmin=, cmax=
    #
    #              90
    #              |  /
    #              | /
    #              |/ ) angle 
    #    180 --------------- 0
    #              |
    #              |
    #              |
    #             270
    #
    # Input : angle, diameter
    #
    # Output : returns horizontal, vertical component
    #
    # added: 29/7/15 by Ralf Hansen
    # modified : 11/3/16 by Ralf Hansen; 
    #               0 line set to horizontal

    # first determine angle is in 0..360
    while angle < 0: angle += 360
    while angle > 360: angle -= 360
    # determine quadrant and calculate
    if 0 <= angle <= 90:
        hmult = np.sin(radians(90 - angle))*hypo
        vmult = np.cos(radians(90 - angle))*hypo
    elif 90 < angle <= 180:
        hmult = -np.sin(radians(angle - 90))*hypo
        vmult = np.cos(radians(angle - 90))*hypo
    elif 180 < angle <= 270:
        hmult = -np.sin(radians(270 - angle))*hypo
        vmult = -np.cos(radians(270 - angle))*hypo
    elif 270 < angle <= 360:
        hmult = np.sin(radians(angle - 270))*hypo
        vmult = -np.cos(radians(angle - 270))*hypo

    return hmult,vmult
    
def wslant(data, dt, dx, wv = 1450):
    'makes geometric travel time resampling upshift corrections'
    
    # INFO:
    # This function takes data array and performs a geomertic correction
    # or time shift based on the defined dx interval, shown for source to 
    # receiver triangulation in a water collumn below.
    #
    # Formula : Actual Time = sqrt ( Measured Time^2 (t) - 
    #                                               Zero Time^2 (.5*dx/wv) )   
    #          where wv = water velocity (1450 default)
    #
    #          t = sqrt ((1/2*(time sx to bx to gx))^2 - (1/2 *(dx / wv))^2)
    #
    #         dx
    #    |-----------|                  
    #____sx_________gx________ water surface
    #          |    /
    #          |   /              
    #          t  /  wv=1475                 
    #          | /
    #__________|/_____________ bathymetry
    #          bx
    #
    #
    # Input : trace data, time incr.[micro s], dx, [optional water velocity]
    #
    # Output : returns shifted trace data
    #
    # added: 8/3/16 by Ralf Hansen
    
    # define dimesion & extend for dimensional handling
    if np.size(data)/len(data) == 1:
        data = [data]

    # define time arrays & variables
    ns = len(data[0])
    dx = float(dx)
    wv = float(wv)
    zero_time = dx/wv*10**6
    t = np.linspace(0, ns-1, num=ns)
    measured_time = t*dt
    actual_index = [0]
    ref_index = [0]
    ref = 0
    
    # generate actual time array
    for i in range(ns):
        # exclude all time before zero time onset
        if measured_time[i] > zero_time:
            index = int(round(
                        np.sqrt((measured_time[i])**2-(zero_time)**2)/dt
                              ))
            actual_index += [index]
            
            # shift sample to "correct" time position
            for j in range(index-ref):
                for k in range(len(data)):
                    data[k][j+ref+1] = data[k][i]
            ref = index
            
    # return to input dimension
    if len(data) == 1:
        data = data[0]

    return data
    
def utm(Lat, Lon, utmZone):
    'Apply UTM projection to infile data. Requires pyproj and uses WGS84'
    # INFO:
    # This function takes Lat and Lon and projected to UTM coordinates of
    # defined zone.
    #
    # Input : Lat, Lon, UTM zone
    #
    # Output : returns projected UTM coordinates
    #
    # added: 21/3/16 by Ralf Hansen
    
    p = Proj(proj='utm', zone=int(utmZone), ellps='WGS84')
    return np.array(p(Lon, Lat)).T  # must be Lon, Lat 
    
