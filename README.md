# geoscience
The Readme serves as a basic overview of the modules available here and their
applications. Each module contains additional subs as described below. 
Written in python 2.7

[Modules]

<scipy>   : Support files. See documentation inside folder tree and online.

<pyproj>  : Support files. See documentation inside folder tree and online.

<Formats> : contains subs for accessing binary data formats, header information
            stored as Seismic Unix headers

    DZT :   for GSSI .dzt format 
            DZT (class) >> y = Formats.DZT.DZT(INFILE)
            
                .read() ! should not be called directly !
                        will read in binary data of INFILE and parse out
                        header information and trace data
                            
                .write(OUTFILE) 
                        will write to OUTFILE binary format defined
                        by .fileformat variable (defaulted to 'su')
                        options are 'sg2','sgy' and 'su'

                .header('HEADER') 
                        returns array values for defined HEADER

                .setheader('HEADER',trace(s))
                        sets values for HEADER fields. Can be array of N 
                        values (N = # traces), Integer value that is applied
                        to all traces, or array of 2 values interpeted as
                        ['tracl', VALUE] to set trace # 'tracl' HEADER value

                .zero(TRACE(S))
                        sets values of given trace = 0. Can be integer for
                        a single trace, or an array of values for multiple
                        traces

                .stream
                        contains the trace data as a numpy array of length =
                        # traces, and length of trace = # samples

                .VARIOUS OTHERS
                        additional variables are assigned during reading and
                        writing, but should not be called

    IMxxx : for Imagenix .851, .852, .81e formats
            Imagenix (class) >> y = Formats.IMxxx.Imagenix(INFILE)
            
                .read() ! should not be called directly !
                        will read in binary data of INFILE and parse out
                        header information and trace data
                            
                .write(OUTFILE) 
                        will write to OUTFILE binary format defined
                        by .fileformat variable (defaulted to 'su')
                        options are 'sg2','sgy' and 'su'

                .header('HEADER') 
                        returns array values for defined HEADER

                .setheader('HEADER',trace(s))
                        sets values for HEADER fields. Can be array of N 
                        values (N = # traces), Integer value that is applied
                        to all traces, or array of 2 values interpeted as
                        ['tracl', VALUE] to set trace # 'tracl' HEADER value

                .zero(TRACE(S))
                        sets values of given trace = 0. Can be integer for
                        a single trace, or an array of values for multiple
                        traces

                .stream
                        contains the trace data as a numpy array of length =
                        # traces, and length of trace = # samples

                .VARIOUS OTHERS
                        additional variables are assigned during reading and
                        writing, but should not be called

    SEGY :  for SEG-Y standard data files
            SEGY (class) >> y = Formats.SEGY.SEGY(INFILE)
            
                .read() ! should not be called directly !
                        will read in binary data of INFILE and parse out
                        header information and trace data
                            
                .write(OUTFILE) 
                        will write to OUTFILE binary format defined
                        by .fileformat variable (defaulted to 'su')
                        options are 'sg2','sgy' and 'su'

                .header('HEADER') 
                        returns array values for defined HEADER

                .setheader('HEADER',trace(s))
                        sets values for HEADER fields. Can be array of N 
                        values (N = # traces), Integer value that is applied
                        to all traces, or array of 2 values interpeted as
                        ['tracl', VALUE] to set trace # 'tracl' HEADER value

                .zero(TRACE(S))
                        sets values of given trace = 0. Can be integer for
                        a single trace, or an array of values for multiple
                        traces

                .stream
                        contains the trace data as a numpy array of length =
                        # traces, and length of trace = # samples

                .VARIOUS OTHERS
                        additional variables are assigned during reading and
                        writing, but should not be called

    SEG2 :  for Geonics Seg2 data files
            SEG2 (class) >> y = Formats.SEG2.SEG2(INFILE)
            
                .read() ! should not be called directly !
                        will read in binary data of INFILE and parse out
                        header information and trace data
                            
                .write(OUTFILE) 
                        will write to OUTFILE binary format defined
                        by .fileformat variable (defaulted to 'su')
                        options are 'sg2','sgy' and 'su'

                .header('HEADER') 
                        returns array values for defined HEADER

                .setheader('HEADER',trace(s))
                        sets values for HEADER fields. Can be array of N 
                        values (N = # traces), Integer value that is applied
                        to all traces, or array of 2 values interpeted as
                        ['tracl', VALUE] to set trace # 'tracl' HEADER value

                .zero(TRACE(S))
                        sets values of given trace = 0. Can be integer for
                        a single trace, or an array of values for multiple
                        traces

                .stream
                        contains the trace data as a numpy array of length =
                        # traces, and length of trace = # samples

                .VARIOUS OTHERS
                        additional variables are assigned during reading and
                        writing, but should not be called

    SU :    for Seismic Unix binary data files
            SU (class) >> y = Formats.SU.SU(INFILE)
            
                .read() ! should not be called directly !
                        will read in binary data of INFILE and parse out
                        header information and trace data
                            
                .write(OUTFILE) 
                        will write to OUTFILE binary format defined
                        by .fileformat variable (defaulted to 'su')
                        options are 'sg2','sgy' and 'su'

                .header('HEADER') 
                        returns array values for defined HEADER

                .setheader('HEADER',trace(s))
                        sets values for HEADER fields. Can be array of N 
                        values (N = # traces), Integer value that is applied
                        to all traces, or array of 2 values interpeted as
                        ['tracl', VALUE] to set trace # 'tracl' HEADER value

                .zero(TRACE(S))
                        sets values of given trace = 0. Can be integer for
                        a single trace, or an array of values for multiple
                        traces

                .stream
                        contains the trace data as a numpy array of length =
                        # traces, and length of trace = # samples

                .VARIOUS OTHERS
                        additional variables are assigned during reading and
                        writing, but should not be called

    tools : contains the various tools used in manipulating the binary format
            files.

            .hdr2bin(TRACE HEADERS, HEADER FILE, FILE FORMAT)
                    writes array of string objects TRACE HEADERS to a format
                    defined in HEADER FILE (Formats.header) and sets any 
                    required headers based on 'su' or 'sgy' FILE FORMAT
                    
            .get_header(HEADERS, FIELD):
                    returns array of values from the HEADER array matching the
                    given FIELD
                    
            .make_SEG2_file_header(HEADER FILE):
                    returns a binary string for writing the file header 
                    information specific to the Geonics SEG2 file format
                    
            .make_SEG2_trace_header(HEADER FILE):
                    returns a binary string for writing the trace header
                    information of the Geonics SEG2 file format
                    
            .parse_arguments()
                    argument parser for use in dealing with the given file
                    formats. Restricts output file formats and sets defaults
                    
            .parse_bit_command(COMMAND, DATA)
                    local human readable command convention parser to deal 
                    with particular bit assignment and test. Takes COMMAND
                    and extracts/manipulates/determines output from binary
                    input DATA
                    
            .set_header(HEADERS, FIELD, VALUES):
                    assigns VALUES to a given FIELD in the HEADER array
                    
            .set_zero(HEADERS, DATA, TRACES(s)):
                    Seeks TRACE(s) in 'tracl' field of HEADERS array and 
                    sets corresponding trace data values in DATA = 0
            
            .write_binary(TRACE HEADERS, DATA, FORMAT, OUTFILE):
                    creates a binary string for output using TRACE HEADERS,
                    DATA, and writes these to OUTFILE in the specified data
                    FORMAT
    
    header : contains the file format header arrays corresponding to the file 
             format classes found in Formats. 
             [LENGTH, STARTING BIT, NAME, TYPE], where TYPE can contain a bit
             parsing command (see .parse_bit_command)
            
            .SEGY_binary_file_header_format
                    SEG-Y binary file format headers
            
            .SU_trace_header_format
                    Seismic Unix binary file format headers
                    
            .DZT_trace_header_format
                    GSSI .dzt binary file format headers

            .SEG2_trace_header_format
                    Geonics SEG-2 binary file format headers
            
            .Im81e_trace_header_format
                    Imagenix Delta-F .81e  binary file format headers
                    
            .Im851_trace_header_format
                    Imagenix .851 "Button" sonar binary file format headers

            .Im852_trace_header_format
                    Imagenix .852 binary file format headers
                    

<Toolbox> : contains subs of tools with various general functionality and 
            applications

    Geometry :  contains various arithmetic approaches regarding geometric 
                data manipulation

            .inc2deg(DATA, ANGLE, **kwargs)
                    takes an arbitrary array of DATA and converts values to
                    degrees based in data min,max. Overall limits = 0,360, 
                    or these limits can be set by user defined input cmin=MIN
                    cmax=MAX. Returns data array of degree values
                    >> [degrees] = inc2deg([data], angle)
            
            .radians(DEGREES)
                    converts DEGREES to radians and returns values
                    >> radian = radians(degrees)
            
            .polar2cartesian(ANGLE, HYPOTENUSE)
                    takes an angle and line length of a polar coordinate
                    system and converts values to cartesian system. 
                    Interprets 0/360 as vertical, 270/90 as -horizontal/
                    +horizontal. Returns vertical,and horizontal component.
                    Sets degrees based in data min,max, limits = 0,360, or 
                    these limits can be set by user defined input min=MIN, 
                    cmax=MAX. Returns vertical, horizontal component
                    >> H, V = polar2cartesian(angle, length)

            .wslant(DATA, DT, DX, wv = 1450)
                    geometric slant correction for a DX source to receiver
                    distance in a water collumn of WATER VELOCITY (wv) = 1450
                    unless user specified. Does the timing correction by 
                    shuffling DATA samples to "correct" time position. 
                    Sensitivity is dependent on DT, the sampling time.
                    DATA can be array or matrix. Returns adjusted data set 
                    >> [data_slant] = Toolbox.Geometry.wslant([data], dt, dx)
            
                
    Data :  contains various data analysis and manipulation methods
    
            grid([DATA, xlim = XLIM, ylim = YLIM, zlim = ZLIM, dx = DX
                    dy = DY, method = METHOD [DEFAULT = 'cubic'], 
                    inputfunction = 'multquadratic' [DEFAULT] (rbf,o/ukrige), 
                 ])
                (class) >> y = Data.grid(**kwargs)
                
                {{INFO}}: 
                
                {{DATA must be an numpy array [X,Y,Z] of numbers                
                
                methods = 'linear', 'nearest', 'cubic', 'rbf', 'okrige', 
                          and 'ukrige'
                inputfunction = (rbf): 'multiquadric', 'inverse', 'gaussian',
                                'linear', 'cubic', 'quintic', 'thin_plate'
                                (o/ukrige): 'linear', 'power', 'gaussian',
                                'spherical','exponential'
                drift = 'regional_linear', 'point_log', 'external_Z
                
                No variables need to be set initially to make use of grid 
                function calls. If variables are set, reference grid function
                is automatically determined for .f, and .x,.y,.z defined.}}

                ._setlimits
                    internal function call to define limits of mesh and data
 
                .mesh(XLIM, YLIM, DX, DY)
                    returns a regular 2D mesh of points based on input limits
                    >> X_mesh, Y_mesh = Data.grid.mesh(XLIM, YLIM, DX, DY)
 
                .linear(X, Y, Z)
                    linear interpolation. Uses Dilauny triangulation.
                    f = Data.grid.linear(X, Y, Z)
 
                .nearest(X, Y, Z)
                    nearest neighbour triangulation
                    f = Data.grid.nearest(X, Y, Z)
 
                .cubic(X, Y, Z)
                    minimum curvature Clough Tocher interpolation approach
                    f = Data.grid.cubic(X, Y, Z)
 
                .rbf(X, Y, Z, [eps = EPSILON], [inputfunction = FUNCTION])
                    input function options:
                        'multiquadric': sqrt((r/self.epsilon)**2+1) [DEFAULT]
                        'inverse': 1.0/sqrt((r/self.epsilon)**2+1)
                        'gaussian': exp(-(r/self.epsilon)**2)
                        'linear': r
                        'cubic': r**3
                        'quintic': r**5
                        'thin_plate': r**2 * log(r)
                    >> f = Data.grid.rbf(X, Y, Z)
                    
                .residual(X, Y)
                    residuals X, Y on refernce grid. If not defined, grid can 
                    be set using .setrefgrid(GRID)
                    >> Data.grid.residual(X,Y)
 
                .setrefgrid(GRID)
                    will set a user defined reference grid if no grid was 
                    defined initially
                    >> Data.grid.setrefgrid(GRID)
 
                .plot(original = FALSE, contour = False)
                    will display reference data and grid for visual inspection
                    Not meant for general presentation purposes. Can only be 
                    called if grid parameters are defined at initial Data.grid
                    call. original/contour = True to show original points or
                    contours
                    >> Data.grid.plot()

