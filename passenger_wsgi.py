import sys
import os

INTERP = "/home/inlinkff/virtualenv/home/3.11/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, '/home/inlinkff/linkedin-content-bank')

from app import app as application