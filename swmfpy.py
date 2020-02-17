#!/usr/bin/env python3
"""swmfpy is a tool to read and visualize SWMF data
"""
__author__ = "Qusai Al Shidi"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Qusai Al Shidi"
__email__ = "qusai@umich.edu"

import datetime as dt
import numpy as np
import pandas as pd


def read_wdc_ae(wdc_filename):
    """Read an AE WDC text file into a dictionary of arrays.

    Parameters:
        wdc_filename: string. Filename of wdc data from
        http://wdc.kugi.kyoto-u.ac.jp/
    Returns:
        dict: {"time": array of datetime objects corresponding to time
                       in UT.
               "al","ae"...: Indices.
              }
    """
    data = {"AL": {"Time": [], "Index": []},
            "AE": {"Time": [], "Index": []},
            "AO": {"Time": [], "Index": []},
            "AU": {"Time": [], "Index": []}}
    with open(wdc_filename) as wdc_file:
        for line in wdc_file:
            ind_data = line.split()
            for minute in range(60):
                str_min = str(minute)
                if minute < 10:
                    str_min = "0" + str_min
                time = dt.datetime.strptime(ind_data[1][:-5]
                                            + ind_data[1][7:-2]
                                            + str_min,
                                            "%y%m%d%H%M")
                data[ind_data[1][-2:]]["Time"] += [time]
                data[ind_data[1][-2:]]["Index"] += [int(ind_data[3+minute])]
    return data


def read_omni_csv(filename, filtering=False, **kwargs):
    """Take an OMNI csv file from cdaweb.sci.gsfc.nasa.gov
    and turn it into a pandas.DataFrame.

    Parameters:
        fnames: dict with filenames from omni .lst files. The keys must be:
            density, temperature, magnetic_field, velocity
        filtering: default=False Remove points where the value
                          is >sigma (default: sigma=3) from mean.

    Returns: pandas.DataFrame object with solar wind data

    Make sure to download the csv files with cdaweb.sci.gsfc.nasa.gov
    the header seperated into a json file for safety.

    This only tested with OMNI data specifically.

    Other Parameters:
        coarseness: default=3, Number of standard deviations above which to
                    remove if filtering=True.
        clean: default=True, Clean the omni data of bad data points

    """
    # Read the csv files and set the index to dates
    colnames = ['Time', 'Bx [nT]', 'By [nT]', 'Bz [nT]',
                'Vx [km/s]', 'Vy [km/s]', 'Vz [km/s]',
                'Rho [n/cc]', 'T [K]']
    with open(filename, 'r') as datafile:
        data = pd.read_csv(datafile, names=colnames, skiprows=1)
    data.set_index(pd.to_datetime(data[data.columns[0]]), inplace=True)
    data.drop(columns=data.columns[0], inplace=True)
    data.index.name = "Time [UT]"

    # clean bad data
    if kwargs.get('clean', True):
        data["By [nT]"] = data["By [nT]"][data["By [nT]"].abs() < 80.]
        data["Bx [nT]"] = data["Bx [nT]"][data["Bx [nT]"].abs() < 80.]
        data["Bz [nT]"] = data["Bz [nT]"][data["Bz [nT]"].abs() < 80.]
        data["Rho [n/cc]"] = data["Rho [n/cc]"][data["Rho [n/cc]"] < 500.]
        data["Vx [km/s]"] = data["Vx [km/s]"][data["Vx [km/s]"].abs() < 2000.]
        data["Vz [km/s]"] = data["Vz [km/s]"][data["Vz [km/s]"].abs() < 1000.]
        data["Vy [km/s]"] = data["Vy [km/s]"][data["Vy [km/s]"].abs() < 1000.]
        data["T [K]"] = data["T [K]"][data["T [K]"] < 1.e7]

    if filtering:
        coarse_filtering(data, kwargs.get('coarseness', 3))
    return data.interpolate().bfill().ffill()


def coarse_filtering(data, coarseness=3):
    """Applies coarse filtering to a pandas.DataFrame"""
    for column in data.columns:
        mean = data[column].abs().mean()
        sigma = data[column].std()
        data[column] = data[data[column].abs() < mean+coarseness*sigma][column]


def write_sw_input(data, outfilename="IMF.dat", enable_rb=True, **kwargs):
    """Writes the pandas.DataFrame into an input file
    that SWMF can read as input IMF (IMF.dat).

    Parameters:
        data: pandas.DataFrame object with solar wind data
        outfilename: The output file name for ballistic solar wind data. \
                (default: "IMF.dat")
        enable_rb: Enables solar wind input for the radiation belt model. \
                (default: True)

    Other paramaters:
        gse: (default=False)
            Use GSE coordinate system for the file instead of GSM default.
    """
    # Generate BATS-R-US solar wind input file
    with open(outfilename, 'w') as outfile:
        outfile.write("CSV files downloaded from ")
        outfile.write("https://cdaweb.gsfc.nasa.gov/\n")
        if kwargs.get('gse', False):
            outfile.write("#COOR\nGSE\n")
        outfile.write("yr mn dy hr min sec msec bx by bz vx vy vz dens temp\n")
        outfile.write("#START\n")
        for index, rows in data.iterrows():
            outfile.write(index.strftime("%Y %m %d %H %M %S") + ' ')
            outfile.write(index.strftime("%f")[:3] + ' ')
            outfile.write(str(rows['Bx [nT]'])[:7] + ' ')
            outfile.write(str(rows['By [nT]'])[:7] + ' ')
            outfile.write(str(rows['Bz [nT]'])[:7] + ' ')
            outfile.write(str(rows['Vx [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Vy [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Vz [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Rho [n/cc]'])[:7] + ' ')
            outfile.write(str(rows['T [K]'])[:7] + ' ')
            outfile.write('\n')
    # Generate RBE model solar wind input file
    if enable_rb:
        with open("RB.SWIMF", 'w') as rbfile:
            # Choose first element as t=0 header (unsure if this is safe)
            rbfile.write(data.index[0].strftime("%Y, %j, %H ")
                         + "! iyear, iday, ihour corresponding to t=0\n")
            swlag_time = None
            if swlag_time in kwargs:
                rbfile.write(str(kwargs["swlag_time"]) + "  "
                             + "! swlag time in seconds "
                             + "for sw travel to subsolar\n")
            # Unsure what 11902 means but following example file
            rbfile.write("11902 data                   "
                         + "P+ NP NONLIN    P+ V (MOM)\n")
            # Quantity header
            rbfile.write("dd mm yyyy hh mm ss.ms           "
                         + "#/cc          km/s\n")
            for index, rows in data.iterrows():
                rbfile.write(index.strftime("%d %m %Y %H %M %S.%f")
                             + "     "
                             + str(rows['Rho [n/cc]'])[:8]
                             + "     "
                             # Speed magnitude
                             + str(np.sqrt(rows['Vx [km/s]']**2
                                           + rows['Vy [km/s]']**2
                                           + rows['Vz [km/s]']**2))[:8]
                             + '\n')


def convert(infile, outfile="IMF.dat"):
    """Start the process of conversion of OMNI file to
    SWMF IMF input file.
    """
    # Write out the header
    outfile.write("OMNI file downloaded from \
                   https://omniweb.gsfc.nasa.gov/\n")
    outfile.write("yr mn dy hr min sec msec bx by bz vx vy vz dens temp\n")
    outfile.write("#START\n")
    # Begin conversion line by line
    for line in infile:
        date = dt.datetime.strptime(line[:14], "%Y %j %H %M")
        correctline = date.strftime("%Y %m %d %H %M %S")\
            + ' 000' + line[14:]
        outfile.write(correctline)
    # Close files
    outfile.close()
    infile.close()


def read_gm_log(filename, colnames=None, index_by_time=True):
    """Make a pandas.DataFrame out of the Dst indeces outputted
    from the GM model log.

    Parameters:
        filename: The filename as a string.
        colnames: Supply the name of the columns whitespace seperated
        index_by_time: Change the index to a time index
    Returns:
        pandas.DataFrame: Of the log file

    Examples:
        # To plot AL and Dst get the log files
        geo = swmfpy.read_gm_log("run/GM/IO2/geoindex_e20140215-100500.log")
        dst = swmfpy.read_gm_log("run/GM/IO2/log_e20140215-100500.log")
        # Then plot using pandas features
        dst["dst_sm"].plot.line()
        geo["AL"].plot.line()
    """
    # If column names were not specified
    if not colnames:
        with open(filename, 'r') as logfile:
            # Usually the names are in the second line
            logfile.readline()
            colnames = logfile.readline().split()
    data = pd.read_fwf(filename, header=None, skiprows=2, names=colnames)
    if index_by_time:
        data.set_index(pd.to_datetime({'year': data['year'],
                                       'month': data['mo'],
                                       'day': data['dy'],
                                       'h': data['hr'],
                                       'm': data['mn'],
                                       's': data['sc']}),
                       inplace=True)
        data.index.names = ['Time [UT]']
    return data


def replace_paramin_option(param_file, replace, output_file="PARAM.in"):
    """Replace options in a PARAM.in file.

    Parameters:
        param_file: String of PARAM.in file name.
        replace: Dictionary of strings with format
              replace["#COMMAND"]["parameter"] = "value"
              This is case sensitive.
        output_file: (default "PARAM.in") The output file to write to.
    Returns:
        A list of lines of the PARAM.in file that would be outputted.

    Example:
        change["#SOLARWINDFILE"]["UseSolarWindFile"] = "T"
        change["#SOLARWINDFILE"]["NameSolarWindFile"] = "new_imf.dat"
        change["#DOAMR"]["DnAmr"] = 200
        # This will overwrite PARAM.in
        replace_paramin_option("PARAM.in.template", change)

    Note, if you have repeat commands this will replace all the repeats.
    """
    # TODO This will replace all for repeat commands.
    with open(param_file, 'rt') as paramin:
        command = None  # Top level #COMMAND
        # Compile lines in a list before editing/writing it
        lines = list(paramin)
        for line_num, line in enumerate(lines):
            words = line.split()
            if words and words[0] in replace.keys():
                command = words[0]  # Current command
            # Start replace once we're in a specified command
            elif command in replace.keys():
                for param, value in replace[command].items():
                    newline = value
                    if param == words[1]:
                        newline += "\t\t\t" + param
                        print("Replacing:", line, "with:", newline)
                        lines[line_num] = newline + '\n'
    # Write the PARAM.in file
    with open(output_file, 'w') as outfile:
        for line in lines:
            outfile.write(line)
    return lines
