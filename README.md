# Info
A small python3 script converting Strava exported .gpx filed to .csv and adding Sun Elevation, Azimuth and estimated Clear Sky Radiation for data visualisation in Houdini etc.

# Install
> pip install -r requirements.txt

# Usage:
Single file convert:
> python gpx2csv.py --file <inputfile.gpx>

Batch convert all files in the supplied folder:
> python gpx2csv.py --folder </path/to/folder>

Help:
> python gpx2csv.py --help