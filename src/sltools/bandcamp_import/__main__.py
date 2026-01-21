#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <sebastien.lemaguer@adaptcentre.ie>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 23 April 2020
"""

# System/default
import sys
import os

# Arguments
import argparse

# Messaging/logging
import traceback
import time
import logging

# data
import pandas as pd

# Regexp
import re

# Zip
from zipfile import ZipFile

# Image
from PIL import Image

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.INFO, logging.DEBUG]

###############################################################################
# Functions
###############################################################################


###############################################################################
# Main function
###############################################################################
def main():
    """Main entry function
    """
    global args

    df = pd.read_csv(args.input_csv, sep=args.separator)

    for r in df.iterrows():
        logger.info("Import \"%s\" from \"%s\"" % (r[1]["Artist"], r[1]["Album"]))

        # Generate directory
        album_dir = "%s/%s/%s - %s" % (args.output_dir, r[1]["Artist"], r[1]["Year"], r[1]["Album"])
        logger.debug("")
        logger.debug("Create directory \"%s\"" % album_dir)
        os.makedirs(album_dir, exist_ok=True)

        # Extract zip
        zip_file = "%s/%s - %s.zip" % (args.input_dir, r[1]["Artist"], r[1]["Album"])
        logger.debug("Extract \"%s\"" % zip_file)
        with ZipFile(zip_file, 'r') as zipObj:
            zipObj.extractall(album_dir)

        # Rename file
        for track in os.listdir(album_dir):
            if not track.endswith(".flac"):
                continue

            m = re.search("([0-9]{2}) (.*.flac)", track)
            if m is None:
                raise Exception("Bad format for track \"%s\"" % track)
            filename = "%s - %s" % (m[1], m[2])

            logger.debug("Rename track \"%s\" -> \"%s\"" % (track, filename))
            os.rename(os.path.join(album_dir, track),
                      os.path.join(album_dir, filename))

        # Generate proper covers
        try:
            image = Image.open('%s/cover.jpg' % album_dir)
        except FileNotFoundError:
            image = Image.open('%s/cover.png' % album_dir)

        image = image.convert("RGB")

        image = image.resize((120, 120))
        image.save('%s/cover_med.jpg' % album_dir)

        image = image.resize((60, 60))
        image.save('%s/cover_small.jpg' % album_dir)


        logger.debug("")
        logger.debug("===============================================================")

###############################################################################
#  Envelopping
###############################################################################
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="")

        # Add options
        parser.add_argument("-l", "--log_file", default=None,
                            help="Logger file")
        parser.add_argument("-s", "--separator", default="\t",
                            help="")
        parser.add_argument("-v", "--verbosity", action="count", default=0,
                            help="increase output verbosity")

        # Add arguments
        parser.add_argument("input_csv", help="The CSV file which contains the meta-information")
        parser.add_argument("input_dir", help="The directory containing the zip files downloaded from bandcamp")
        parser.add_argument("output_dir", help="The root directory which will contain the music unpacked and organized")

        # Parsing arguments
        args = parser.parse_args()

        # create logger and formatter
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Verbose level => logging level
        log_level = args.verbosity
        if (args.verbosity >= len(LEVEL)):
            log_level = len(LEVEL) - 1
            logger.setLevel(log_level)
            logger.warning("verbosity level is too high, I'm gonna assume you're taking the highest (%d)" % log_level)
        else:
            logger.setLevel(LEVEL[log_level])

        # create console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # create file handler
        if args.log_file is not None:
            fh = logging.FileHandler(args.log_file)
            logger.addHandler(fh)

        # Debug time
        start_time = time.time()
        logger.debug("start time = " + time.asctime())

        # Running main function <=> run application
        main()

        # Debug time
        logger.debug("end time = " + time.asctime())
        logger.debug('TOTAL TIME IN MINUTES: %02.2f' %
                     ((time.time() - start_time) / 60.0))

        # Exit program
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit:  # sys.exit()
        pass
    except Exception as e:
        logging.error('ERROR, UNEXPECTED EXCEPTION')
        logging.error(str(e))
        traceback.print_exc(file=sys.stderr)
        sys.exit(-1)
