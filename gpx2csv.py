#!/usr/bin/python
 
# gpx 2 csv
# Jonas Otto - helloworld@jonasotto.de
# Converting GPX files exported from Strava .csv files
# adding Sun Elevation, Azimuth and estimated Clear Sky Radiation
# for data visualisation in Houdini etc.

import csv

from datetime import datetime as dt
from datetime import timezone
import math
import re

import argparse
import os
import sys

def convert(file_path):
    file_name = os.path.basename(file_path)
    without_extension = ".".join(file_name.split(".")[:-1])
    file_path_only = os.path.dirname(file_path)
    print_info("Starting conversion of %s." % file_name)
    start = dt.now()
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        csv_data = []
        
        start_time = None
        for track in gpx.tracks:
            for segment in track.segments:
                for i, point in enumerate(segment.points):
                    date = point.time
                    date_string = date.strftime("%Y-%m-%d %H:%M:%S")
                    date_timestamp = date.replace(tzinfo=timezone.utc).timestamp()
                    if not start_time:
                        start_time = date_timestamp
                    time_offset = date_timestamp - start_time
                    lat = point.latitude
                    long = point.longitude
                    alt = get_altitude(lat, long, date)
                    azi = get_azimuth(lat, long, date)
                    ele = point.elevation
                    extensions = {"atemp": None, "hr": None, "cad": None, "power": None}
                    
                    for ext in point.extensions:
                        children = list(ext)
                        if len(children) > 0:
                            for extchild in list(ext):
                                tag = re.sub(r'{.*}', '', extchild.tag).strip()
                                value = extchild.text
                                if tag in extensions:
                                    extensions[tag] = value
                        else:
                            if ext.tag in extensions:
                                    extensions[ext.tag] = ext.text
                            
                    speed = segment.get_speed(i)
                    radi = radiation.get_radiation_direct(date, alt)
                    csv_row = [lat, long, ele, extensions["atemp"], extensions["hr"], extensions["cad"], extensions["power"], speed, alt, azi, radi, date_string, date_timestamp, time_offset] 
                    csv_data.append(csv_row)
        
        csv_name = "%s.csv" % (without_extension)
        csv_file_path = os.path.join(file_path_only, csv_name)
        with open(csv_file_path, 'w', newline='') as csv_file:
            wr = csv.writer(csv_file)
            header = ["latitude", "longitude", "elevation", "temperature", "heart_rate", "cadence", "power", "speed_ms", "sun_altitude", "sun_azimuth", "sun_radiation", "date", "timestamp", "time_offset"]
            wr.writerow(header)
            for row in csv_data:
                wr.writerow(row)

    end = dt.now()
    duration = end - start
    mins = duration.total_seconds() / 60.0
    print_info("Finised converting %s" % file_name)
    print_info("Processing time: %f minutes" % mins)
    print_line()

def get_gpxfiles_from_folder(folder_path):
    files = os.listdir(folder_path)
    gpxfiles = [os.path.join(folder_path,file) for file in files if file.endswith(".gpx")]
    return gpxfiles

def main():
    start = dt.now()
    
    parser = argparse.ArgumentParser(description='Converting GPX files exported from Strava .csv files for data visualisation in Houdini etc.')
    parser.add_argument('--file', help='A single .gpx file to convert')
    parser.add_argument('--folder', help='A folder of .gpx files to batch convert')

    args = parser.parse_args()

    gpxfile = args.file
    gpxFolder = args.folder

    files_to_convert = []

    if gpxFolder is None and gpxfile is not None:
        # single file conversion
        print_info("Attempting a single file conversion")
        files_to_convert.append(gpxfile)
    elif gpxfile is None and gpxFolder is not None:
        # batch conversion
        print_info("Attempting a batch file conversion")
        files_to_convert = get_gpxfiles_from_folder(gpxFolder)
    elif gpxfile is None and gpxFolder is None:
        # you retard did it wrong
        print_warning("Please supply a file or a folder.")
        print_warning("Run python gpx2csv.py --help for more information.")
        exit()
    else:
         # you retard did it wrong
        print_warning("Please only supply a file OR a folder. Not both.")
        print_warning("Run python gpx2csv.py --help for more information.")
        exit()
    
    print_info("Found %d .gpx files to convert." % (len(files_to_convert)) )
    
    for i,file in enumerate(files_to_convert):
        print_info("%i / %i" % (i, len(files_to_convert)))
        convert(file)
    end = dt.now()
    duration = end - start
    mins = duration.total_seconds() / 60.0
    print_info("Finished converting all .gpx files to .csv files.")
    print_info("Processing time: %f minutes" % mins)
    print_info("You can find all generated .csv files next to their originals")

def print_line():
    print("----------------------------------------------------------------------------------")

def print_info(info_text):
    #prints in green
    print('\033[92m' + info_text + '\033[0m')

def print_warning(warning_text):
    #prints in red
    print('\033[91m' + warning_text + '\033[0m')

#os.system('color')
print_line()

try:
    from pysolar.solar import *
except ImportError as error:
    print_warning("Error: Couldn't import the pysolar library.")
    print_warning("Please install via pip install -r requirements.txt or pip install pysolar.")
    print_line()
    exit()

try:
    import gpxpy
except ImportError as error:
    print_warning("Error: Couldn't import the gpxpy library.")
    print_warning("Please install via pip install -r requirements.txt or pip install gpxpy.")
    print_line()
    exit()

if __name__ == "__main__":
   main()