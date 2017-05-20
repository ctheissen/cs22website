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

from glob import glob
import os
import shutil

from jinja2 import Environment, FileSystemLoader

# Generate html
env = Environment(loader=FileSystemLoader('.'))

pagelist = glob('pagesrc/*html')
''' Not foolproof!
The navigation bar is defined in templates/basic.html
and I need to sync that with the content of the src directory by hand
'''

outpath = 'html'

if not os.path.exists(outpath):
    os.makedirs(outpath)

for page in pagelist:
    print("Working on {0}".format(page))
    template = env.get_template(page)
    with open(os.path.join(outpath, os.path.basename(page)), "w") as html_out:
        html_out.write(template.render().encode('utf-8'))

# copy several directories verbatim
for d in ['css', 'fonts', 'images', 'js', 'icons']:
    outdir = os.path.join(outpath, d)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    filelist = glob(os.path.join(d, '*'))
    for f in filelist:
        shutil.copy(f, outdir)

print("Done. Website is in directory: {}.".format(outpath))
