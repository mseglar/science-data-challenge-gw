# Author: Monica Seglar-Arroyo
#!/usr/bin/env python3

import os
import time
import argparse
import datetime
from six.moves import configparser
import pytz
import pandas as pd
import numpy as np
import six
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import ascii
from astropy.table import Table

import sys

from tilepy.include.CampaignDefinition import ObservationParameters
from tilepy.include.Observatories import CTASouthObservatory, CTANorthObservatory
from tilepy.include.TilingDetermination import PGWinFoV
from tilepy.include.ObservationScheduler import GetSchedule
from tilepy.include.PointingPlotting import LoadPointingsGW
from datetime import timedelta

sys.path.append("/data/cta/users-ifae/mseglara/cta-gwfollowup-simulations")

from TimeOptimisationTools import (
    SelectObservatory_fromHotspot,
    ProducePandasSummaryFile,
    PointingPlottingGWCTA,
    PGWonFoV_WindowOptimisation,
    ProducePandasSummaryFile_NoObservation,
    EnsureList,
)

if six.PY2:
    ConfigParser = configparser.SafeConfigParser
else:
    ConfigParser = configparser.ConfigParser

config_default_file = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "configs/sdc.ini"
)

###########################
#####    Parsing  ######
###########################

parser = argparse.ArgumentParser(
    description="Start the CTAO tiling simulation with O5 sensitivity for the Science Data Challenge"
)
parser.add_argument(
    "index",
    metavar="ID",
    help="the event number which is used to connect all the inputs",
)
parser.add_argument(
    "-c",
    metavar="observatory configuration",
    help="observatory configuration, either alpha or omega",
    default="alpha",
)
parser.add_argument("-i", metavar="input path", help="Path to the input datasets")
parser.add_argument("-o", metavar="output path", help="Path to the output folder")
parser.add_argument(
    "-params",
    metavar="configuration file",
    default=config_default_file,
    help="file holding the main parameters (default: %(default)s)",
)
parser.add_argument("-ct", metavar="config tag", help="Config Tag")
parser.add_argument(
    "-t", metavar="type of exposure", help="Two options = fixed or variable"
)
parser.add_argument(
    "-lookup_table",
    metavar="lookup_table",
    default=None,
    help="Default is None. If you want to use a lookup table, please provide the path to the file",
)
args = parser.parse_args()

sdcID = int(args.index)
conf = args.c
DATASET_PATH = args.i  # = os.path.abspath(".").rsplit("/",1)[0]
OUTPUT_PATH = args.o
# WRK_PATH = args.path  # Path where the Python script is
cfgFile = args.params
configTag = args.ct + "_" + args.t
exposureType = args.t

# Load libraries
datasetDir = DATASET_PATH
outDir = OUTPUT_PATH + "/PGWonFoV"
if not os.path.exists(outDir):
    os.makedirs(outDir)

start = time.time()

###########################
#####    SDC Files     ####
###########################

InputFileName_SDC = datasetDir + "CTAO-SDC-GW-metadata.csv"
InputList = pd.read_csv(InputFileName_SDC, delimiter=",")

print(InputList.columns)
# BNS ID from simulation set
ID = InputList["model_id"].iloc[sdcID]
GWname = InputList["superevent_id"].iloc[sdcID]
InputTime = InputList["timestamp_utc"][sdcID]

###########################
####   BNS-GRB Files   ####
###########################

# InputFileName = datasetDir + '/BNS-GW-new.txt'
InputFileName = datasetDir + "O5/bns_astro/injections.dat"

InputList = pd.read_csv(InputFileName, delimiter="\t")
Source = SkyCoord(
    ra=InputList["longitude"][ID] * u.radian,
    dec=InputList["latitude"][ID] * u.radian,
    frame="icrs",
)

# GW file
BNSname = str(ID)
GWFile = datasetDir + "O5/bns_astro/allsky/" + BNSname + ".fits"

#################################

print(" ")
print(
    "==========================================================================================="
)
print("Starting the CTA pointing calculation with the following parameters\n")
print("InputFile: ", InputFileName)
BNSname = str(ID)
print("ID to be analyzed: ", sdcID, "BNS ID:", ID)
print("GW ID to be analyzed: ", GWname, "BNS name:", BNSname)
print("Source Coordinates: ", Source)
print("Date: ", InputTime)
print("Configuration: ", cfgFile)
print("Output: ", outDir)
print(
    "==========================================================================================="
)
print(" ")

ObservationTime0 = datetime.datetime.strptime(
    InputTime.split(".")[0], "%Y-%m-%d %H:%M:%S"
)
ObservationTime0 = pytz.utc.localize(ObservationTime0)


obspar = ObservationParameters()
obspar.event_name = sdcID
obspar.skymap = GWFile
obspar.obsTime = ObservationTime0
obspar.outDir = outDir
obspar.from_configfile(cfgFile)


#################################
UseObs = SelectObservatory_fromHotspot(GWFile)

# Observatory
if UseObs == "south":
    print("Observed form the", UseObs)
    obspar.obs_name = UseObs
    obspar.lon = CTASouthObservatory().Lon
    obspar.lat = CTASouthObservatory().Lat
    obspar.height = CTASouthObservatory().Height
    obspar.location = CTASouthObservatory().location
else:
    print("Observed from the", UseObs)
    obspar.obs_name = UseObs
    obspar.lon = CTANorthObservatory().Lon
    obspar.lat = CTANorthObservatory().Lat
    obspar.height = CTANorthObservatory().Height
    obspar.location = CTANorthObservatory().location

print(obspar)

# Add slewing to time
obspar.obsTime = ObservationTime0 + timedelta(seconds=obspar.minSlewing)
print(obspar.obsTime, ObservationTime0)
GetSchedule(obspar)
resultsPath = f"{obspar.outDir}/{sdcID}/SuggestedPointings_2DProbOptimisation.txt"

if os.path.exists(resultsPath):
    timeObs, coordinates, pgw = LoadPointingsGW(resultsPath)
    SuggestedPointings = Table(
        [timeObs, coordinates.ra.deg, coordinates.dec.deg, pgw],
        names=["Observation Time UTC", "RA[deg]", "DEC[deg]", "PGW"],
    )
    totalPoswindow = len(SuggestedPointings)
    SuggestedPointings["delay"] = [
        (
            pytz.utc.localize(
                (
                    datetime.datetime.strptime(
                        SuggestedPointings["Observation Time UTC"][i],
                        "%Y-%m-%d %H:%M:%S",
                    )
                )
            )
            - ObservationTime0
        ).total_seconds()
        for i in range(totalPoswindow)
    ]
    SuggestedPointings["duration"] = [
        obspar.duration * 60 for _ in range(totalPoswindow)
    ]  # from minutes to seconds
    true_array = ["True" for _ in range(totalPoswindow)]
    SuggestedPointings["ObsInfo"] = true_array
    SuggestedPointings["Observatory"] = [obspar.obs_name for _ in range(totalPoswindow)]
else:
    print("No observations are scheduled for this event")

end = time.time()
print("Execution time: ", end - start)

dirNameSchD = outDir + "/ScheduledObs_Detailed"
if not os.path.exists(dirNameSchD):
    os.makedirs(dirNameSchD)


try:
    SuggestedPointings
except NameError:
    # Variable is not defined
    print("SuggestedPointings is not defined.")
    ProducePandasSummaryFile_NoObservation(sdcID, outDir, configTag)
else:
    # Variable is defined
    print("SuggestedPointings is defined.")
    pointingsFile = "%s/%s.txt" % (dirNameSchD, GWname)
    ascii.write(SuggestedPointings, pointingsFile, overwrite=True, fast_writer=False)

    print("===== PRODUCING SUMMARY FILE =======")

    ProducePandasSummaryFile(
        Source, SuggestedPointings, sdcID, obspar, "GW", datasetDir, outDir, configTag
    )

    if totalPoswindow != 0 and obspar.doPlot == True:
        PointingPlottingGWCTA(GWFile, sdcID, outDir, SuggestedPointings, obspar)
