#!./bin/python
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

# The format of the 400 byte long binary file header.
SEGY_binary_file_header_format = [
    # [length, start byte, name, mandatory]
    [3200, 0, 'unassigned_0','b'],
    [4, 3200, 'job_id','i'],
    [4, 3204, 'line_nr','i'],
    [4, 3208, 'reel_nr','i'],
    [2, 3212, 'nr_tr_in_ensemble','H'],
    [2, 3214, 'nr_of_auxiliary_traces_per_ensemble','H'],
    [2, 3216, 'dt','H'],
    [2, 3218, 'dt_field_recording','H'],
    [2, 3220, 'ns','H'],
    [2, 3222, 'ns_field_recording','H'],
    [2, 3224, 'data_sample_format_code','H'], 
    [2, 3226, 'ensemble_fold','H'],
    [2, 3228, 'trace_sorting_code','H'],
    [2, 3230, 'vertical_sum_code','H'],
    [2, 3232, 'sfs','H'],
    [2, 3234, 'sfe','H'],
    [2, 3236, 'slen','H'],
    [2, 3238, 'styp','H'],
    [2, 3240, 'trace_number_of_sweep_channel','H'],
    [2, 3242, 'stas','H'],
    [2, 3244, 'stae','H'],
    [2, 3246, 'ttype','H'],    
    [2, 3248, 'correlated_data_traces','H'],
    [2, 3250, 'binary_gain_recovered','H'],
    [2, 3252, 'amplitude_recovery_method','H'],
    [2, 3254, 'measurement_system','H'],
    [2, 3256, 'impulse_signal_polarity','H'],
    [2, 3258, 'vibratory_polarity_code','H'],
    [240, 3260, 'unassigned_1','b'],
    [2, 3500, 'seg_y_format_revision_number','H'],
    [2, 3502, 'fixed_length_trace_flag','H'],
    [2, 3504, 'nr_of_hdr_records_2follow','H'],
    [94, 3506, 'unassigned_2','b']]

SU_trace_header_format = [
    # [length, start_byte, name]
    # Special type enforces a different format while unpacking using struct.
    [4, 0, 'tracl','i'],
    [4, 4, 'tracr','i'],
    [4, 8, 'fldr','i'],
    [4, 12, 'tracf','i'],
    [4, 16, 'ep','i'],
    [4, 20, 'cdp','i'],
    [4, 24, 'cdpt','i'],
    [2, 28, 'trid','H'],
    [2, 30, 'nvs','H'],
    [2, 32, 'nhs','H'],
    [2, 34, 'duse','H'],
    [4, 36, 'offset','i'],
    [4, 40, 'gelev','i'],
    [4, 44, 'selev','i'],
    [4, 48, 'sdepth','i'],
    [4, 52, 'gdel','i'],
    [4, 56, 'sdel','i'],
    [4, 60, 'swdep','i'],
    [4, 64, 'gwdep','i'],
    [2, 68, 'scalel','H'],
    [2, 70, 'scalco','H'],
    [4, 72, 'sx','i'],
    [4, 76, 'sy','i'],
    [4, 80, 'gx','i'],
    [4, 84, 'gy','i'],
    [2, 88, 'counits','H'],
    [2, 90, 'wevel','H'],
    [2, 92, 'swevel','H'],
    [2, 94, 'sut','H'],
    [2, 96, 'gut','H'],
    [2, 98, 'sstat','H'],
    [2, 100, 'gstat','H'],
    [2, 102, 'tstat','H'],
    [2, 104, 'laga','H'],
    [2, 106, 'lagb','H'],
    [2, 108, 'delrt','H'],
    [2, 110, 'muts','H'],
    [2, 112, 'mute','H'],
    [2, 114, 'ns','H'],
    [2, 116, 'dt','H'],
    [2, 118, 'gain','H'],
    [2, 120, 'igc','H'],
    [2, 122, 'igi','H'],
    [2, 124, 'corr','H'],
    [2, 126, 'sfs','H'],
    [2, 128, 'sfe','H'],
    [2, 130, 'slen','H'],
    [2, 132, 'styp','H'],
    [2, 134, 'stas','H'],
    [2, 136, 'stae','H'],
    [2, 138, 'ttype','H'],
    [2, 140, 'aff','H'],
    [2, 142, 'afs','H'],
    [2, 144, 'nff','H'],
    [2, 146, 'nfs','H'],
    [2, 148, 'lcutf','H'],
    [2, 150, 'hcutf','H'],
    [2, 152, 'lcuts','H'],
    [2, 154, 'hcuts','H'],
    [2, 156, 'year','H'],
    [2, 158, 'day','H'],
    [2, 160, 'hour','H'],
    [2, 162, 'minute','H'],
    [2, 164, 'second','H'],
    [2, 166, 'time_basis_code','H'],
    [2, 168, 'trace_weighting_factor','H'],
    [2, 170, 'geognofroll','H'],
    [2, 172, 'geognoftrstart','H'],
    [2, 174, 'geogrnoftrlast','H'],
    [2, 176, 'gap_size','H'],
    [2, 178, 'otataper','H'],
    [4, 180, 'gxtr','i'],
    [4, 184, 'gytr','i'],
    [4, 188, 'stacktr','i'],
    [4, 192, 'stackcrossid','i'],
    [4, 196, 'shotn','i'],
    [2, 200, 'scalartoshotpoint','H'],
    [2, 202, 'trunit','H'],
    [4, 204, 'transmant','i'],
    [2, 208, 'transexp','H'],
    [2, 210, 'transunits','H'],
    [2, 212, 'devtrid','H'],
    [2, 214, 'scalet','H'],
    [2, 216, 'sxorient','H'],
    [4, 218, 'epdirmant','i'],
    [2, 222, 'epdirex','H'],
    [4, 224, 'smant','i'],
    [2, 228, 'sexp','H'],
    [2, 230, 'sunit','H'],
    [8, 232, 'unassigned','b']]


DZT_trace_header_format = [
    [2, 0, 'channel_on', 'H'],
    [2, 2, 'data_offset', 'H'],
    [2, 4, 'ns', 'H'],
    [2, 6, 'data_bits', 'H'],
    [2, 8, 'bin_offset', 'H'],
    [4, 10, 'scans_sec', 'f'],
    [4, 14, 'scans_meter', 'f'],
    [4, 18, 'm_mark', 'f'],
    [4, 22, 'pos_ns', 'f'],
    [4, 26, 'range_ns', 'f'],
    [2, 30, 'scan_pass', 'H'],
    [4, 32, 'date_c', 'x'],
    [4, 36, 'date_m', 'x'],
    [2, 40, 'gain_offset', 'H'],
    [2, 42, 'gain_size', 'H'],
    [2, 44, 'text_offset', 'H'],
    [2, 46, 'text_size', 'H'],
    [2, 48, 'hist_offset', 'H'],
    [2, 50, 'hist_size', 'H'],
    [2, 52, 'channel_num', 'H'],
    [4, 54, 'dia_const', 'f'],
    [4, 58, 'pos_top', 'f'],
    [4, 62, 'range', 'f'],
    [1, 97, 'data_type', 'c'],
    [14, 98, 'antenna', 'c'],
    [2, 112, 'ch_mask', 'H'],
    [12, 114, 'file_name', 'c'],
    [2, 126, 'checksum', 'H']];


SEG2_trace_header_format = [
    [2, True, True, 'ALIAS_FILTER', '3333.33 0', 1,'aff afs'], # aff and aft
    [1, True, True, 'AMPLITUDE_RECOVERY', 'NONE', 1, 'stackcrossid'], 
    # bytes 192-194
    [1, True, True, 'CHANNEL_NUMBER', '0', 1, 'tracl'], # 1 to max geophones
    [1, True, True, 'DELAY', '0.000', 1000, 'tstat'], # if using delay
    [1, True, True, 'DESCALING_FACTOR', '4.270400E-005', 1, 
     'igc'],
    # for 36 DB; 1.698500E-005 for 24 DB
    [2, True, True, 'DIGITAL_HIGH_CUT_FILTER', '0 0', 1, 'hcutf hcuts'], 
    # contains  hcutf & hcuts, byte 150-152, 154-156
    [2, True, True, 'DIGITAL_LOW_CUT_FILTER', '0 0', 1, 'lcutf lcuts'],
    # contains lcutf & lcuts
    [1, True, True, 'FIXED_GAIN', '36 DB', 1, 'igc'], 
    # or 24; see DESCALING FACTOR
    [1, True, True, 'LINE_ID', '0', 1, 'tracr'], 
    # spread id; stored in tracr (bytes 5-8) 
    [2, True, True, 'LOW_CUT_FILTER', '0 0', 1, 'lcutf lcuts'],
    [1, True, True, 'NOTCH_FREQUENCY', '0', 1, 'nff'],
    [1, True, True, 'RAW_RECORD', 'NONE', 0, 'stacktr'], 
    # directory, written to bytes 188-192
    [1, True, True, 'RECEIVER_LOCATION', '0.00', 100, 'gx'], # gx
    [1, True, True, 'SAMPLE_INTERVAL', '0.000125', 1000000, 'dt'], # in sec
    [1, True, True, 'SHOT_SEQUENCE_NUMBER', 'NONE', 1, 'fldr'], # file name
    [1, True, True, 'SKEW', '0.00', 0, 'transmant'], 
    # not preserved
    [1, True, True, 'SOURCE_LOCATION', '-85.00', 100, 'sx'], # sx
    [1, False, True, 'COMPANY', 'Geometrics', 0, 'string'], # default
    [1, False, True, 'INSTRUMENT', 
     'GEOMETRICS SEISMODULES CONTROLLER 0000', 0, 'string'], # default
    [1, False, True, 'JOB_ID', '0000', 0, 'string'],
    [1, False, True, 'OBSERVER', 'Observer', 0, 'string'], # default
    [1, False, True, 'TRACE_SORT', 'AS_ACQUIRED', 0, 'string'], # default
    [1, False, True, 'UNITS', 'METERS', 0, 'string'],
    [1, True, False, 'DISPLAY_SCALE', '87', 1, 'scalet'],
    [1, False, False, 'BASE_INTERVAL', '5.00', 100, 'string'],
    [1, False, False, 'SHOT_INCREMENT', '0.00', 100, 'string'],
    [1, False, False, 'PHONE_INCREMENT', '0.00', 100, 'string'],
    [1, False, False, 'AGC_WINDOW', '0', 1, 'string'],
    [2, False, False, 'DISPLAY_FILTERS', '0 0', 1, 'string string']] 
    
Im81e_trace_header_format = [
    # [length, starting bit, name, type]
    # 8 bit data only
    [3, 0, 'type','c'],
    [1, 3, 'ntoreadindex','b'],
    [11, 8, 'date','c'],
    [1, 19, 'unassigned', 'b'],
    [8, 20, 'time','c'],
    [9, 28, 'unassigned', 'b'],
    [1, 37, 'head_id', 'c'],
    [1, 38, 'mode', 'b'],
    [1, 39, 'gain','b'],
    [3, 40, 'unassigned', 'b'],
    [1, 43, 'absorption', 'x_rd7ca10'],
    [1, 44, 'data_bits', 'x_rdo3+5'],
    [1, 44, 'logF', 'x_rdo0+2'],
    [1, 45, 'pulse_length', 'b'],
    [1, 46, 'profile', 'b'],
    [24, 47, 'header_text', 'c'],
    [29, 71, 'unassigned', 'b'],
    [3, 100, 'device_designation', 'c'],
    [1, 103, 'head_id', 'c'],
    [1, 104, 'serial_status', 'b'],
    [2, 105, 'unassigned', 'b'],
    [1, 107, 'range', 'b'],
    [1, 108, 'profile_low_range', 'x_rd6'],
    [1, 109, 'profile_low_range', 'x_rdo1+6'],
    [3, 110, 'unassigned', 'b'] ];


Im851_trace_header_format = [
    # [length, starting bit, name, type]
    # 8 bit data only
    [3, 0, 'type','c'],
    [1, 3, 'ntoreadindex','b'],
    [2, 4, 'total_bytes', 'x_rd7d7'],
    [2, 6, 'ntoread', 'x_rd7d7'],
    [11, 8, 'date','c'],
    [8, 20, 'time','c'],
    [1, 28, 'unassigned', 'b'],
    [3, 29, 'hun_s','c'],
    [5, 32, 'unassigned', 'b'],
    [1, 37, 'dirxdcrmodstep', 'b'],
    [1, 38, 'gain','b'],
    [4, 39, 'unassigned', 'b'],
    [1, 43, 'absorption', 'b'],
    [1, 44, 'pulse_length', 'b'],
    [1, 45, 'profile', 'b'],
    [2, 46, 'water_velocity', 'x_id7=0e1500_id7=1erd6d7ct10'],
    [32, 48, 'header_text', 'c'],
    [2, 80, 'ROV_depth', 'x_id7=0e0_id7=1erd6d7ct10'],
    [1, 82, 'ROV_units', 'c'],
    [2, 83, 'ROV_heading', 'x_id7=0e0_id7=1erd6d7ct10'],
    [2, 85, 'ROV_counter', 'x_id7=0e0_id7=1erd6d7cs100'],
    [1, 87, 'operating_freq' , 'b'],
    [12, 88, 'unassigned', 'b'],
    [3, 100, 'device_designation', 'c'],
    [1, 103, 'head_id', 'c'],
    [1, 104, 'serial_status', 'b'],
    [1, 105, 'head_low', 'x_rd6'],
    [1, 106, 'head_high', 'x_rdo1+5'],
    [1, 106, 'step_direction', 'x_rdo6'],
    [1, 107, 'range', 'b'],
    [2, 108, 'unassigned', 'b'] ];    
    
Im852_trace_header_format = [
    # [length, starting bit, name, type]
    # 8 bit data only
    [3, 0, 'type','c'],
    [1, 3, 'ntoreadindex','b'],
    [2, 4, 'total_bytes', 'x_rd7d7'],
    [2, 6, 'ntoread', 'x_rd7d7'],
    [11, 8, 'date','c'],
    [8, 20, 'time','c'],
    [1, 28, 'unassigned', 'b'],
    [3, 29, 'hun_s','c'],
    [5, 32, 'unassigned', 'b'],
    [1, 37, 'dirxdcrmodstep', 'b'],
    [1, 38, 'gain','b'],
    [1, 39, 'sector_size', 'x_rd7ct3'],
    [1, 40, 'train_angle', 'x_rd7ct3'],
    [1, 41, 'unassigned', 'b'],
    [1, 42, 'unassigned', 'b'],
    [1, 43, 'unassigned', 'b'],
    [1, 44, 'pulse_length', 'b'],
    [1, 45, 'profile', 'b'],
    [2, 46, 'water_velocity', 'x_id7=0e1500_id7=1erd6d7ct10'],
    [32, 48, 'header_text', 'c'],
    [2, 80, 'ROV_depth', 'x_id7=0e0_id7=1erd6d7ct10'],
    [1, 82, 'ROV_units', 'c'],
    [2, 83, 'ROV_heading', 'x_id7=0e0_id7=1erd6d7ct10'],
    [2, 85, 'ROV_counter', 'x_id7=0e0_id7=1erd6d7cs100'],
    [1, 87, 'operating_freq' , 'b'],
    [1, 88, 'head_id', 'c'],
    [11, 89, 'unassigned', 'b'],
    [3, 100, 'device_designation', 'c'],
    [1, 103, 'head_id', 'c'],
    [1, 104, 'serial_status', 'b'],
    [1, 105, 'head_low', 'x_rd6'],
    [1, 106, 'head_high', 'x_rdo1+5'],
    [1, 106, 'step_direction', 'x_rdo6'],
    [1, 107, 'range', 'b'],
    [2, 108, 'unassigned', 'b'] ];
    
SICK_trace_header_format = [
    [0, 'pseudo_angle'],
    [1, 'year'],
    [2, 'month'],
    [3, 'day'],
    [4, 'hour'],
    [5, 'minute'],
    [6, 'second'],
    [7, 'microseconds']  ]

