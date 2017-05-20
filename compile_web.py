# -*- coding: utf-8 -*-
'''Compile professional homepage

This script compiles my professional homepage.
It uses Jinja2 templates. There is a general template in /templates
The individual files are made with template inheritance in the /src directory.
So far, no actual python code is required to fill values in the templates.
The navigation bar is defined in templates/basic.html and it is assumed that
the number of files in /src matches what is defined in basic.html.

This script needs to be executed in the exact directory where it is now,
because it copies pdfs from posters and talks and the path to all those
is given relative to the current directory.

Call as:

python homepage.py

The output will be written to the /html folder that can be removed later.
'''
from __future__ import print_function

import argparse
from glob import glob
import os
import shutil

from jinja2 import Environment, FileSystemLoader


parser = argparse.ArgumentParser(description='Generate webpages for CS20. We want to generate statics pages for simplicity, but might read in some database (e.g. the database of abstracts) when doing so.')
parser.add_argument('outpath',
                    help='base directory for output')

args = parser.parse_args()

# Generate html
env = Environment(loader=FileSystemLoader('.'))

pagelist = glob('pagesrc/*html')
''' Not foolproof!
The navigation bar is defined in templates/basic.html
and I need to sync that with the content of the src directory by hand
'''

if not os.path.exists(args.outpath):
    os.makedirs(args.outpath)

for page in pagelist:
    print("Working on {0}".format(page))
    template = env.get_template(page)
    with open(os.path.join(args.outpath, os.path.basename(page)), "w") as html_out:
        html_out.write(template.render().encode('utf-8'))

# copy several directories verbatim
for d in ['css', 'fonts', 'images', 'js', 'icons', 'maps']:
    outdir = os.path.join(args.outpath, d)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    filelist = glob(os.path.join(d, '*'))
    for f in filelist:
        shutil.copy(f, outdir)

print("Done. Website is in directory: {}.".format(args.outpath))
