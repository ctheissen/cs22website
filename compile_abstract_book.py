# -*- coding: utf-8 -*-
'''Compile professional homepage

This script compiles the CS20 homepage.
It uses Jinja2 templates. There is a general template in /templates

This script needs to be executed in the exact directory where it is now,
because it uses relative input paths.

'''
import argparse
import os
import shutil
import subprocess

from jinja2 import Environment, FileSystemLoader, select_autoescape

import pagepy.contributions

parser = argparse.ArgumentParser(description='Generate webpages for CS20. We want to generate statics pages for simplicity, but might read in some database (e.g. the database of abstracts) when doing so.')
parser.add_argument('outpath',
                    help='base directory for output')
parser.add_argument('-a', '--abstracts',
                    default='../data/abstracts.csv',
                    help='csv file with abstracts')

args = parser.parse_args()

# Generate html
env = Environment(loader=FileSystemLoader(['templates']),
                  autoescape=select_autoescape(['html']))

if not os.path.exists(args.outpath):
    os.makedirs(args.outpath)

data = pagepy.contributions.data(**vars(args))

tex_templates = ['abstractbook-long.tex']
images = ['print_images/Logoround-04.png']

for tempfile in tex_templates:
    template = env.get_template(tempfile)
    with open(os.path.join(args.outpath, tempfile), "w") as tex_out:
        tex_out.write(template.render(**data))

for f in images:
    shutil.copy(f, args.outpath)

for template in tex_templates:
    out = 'Rerun'
    while 'Rerun' in str(out):
        latex = subprocess.Popen(['pdflatex', '-interaction=nonstopmode',
                                  os.path.join(args.outpath, template)],
                                 cwd=args.outpath,
                                 stdout=subprocess.PIPE)
        out, err = latex.communicate()
