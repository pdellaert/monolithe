# -*- coding: utf-8 -*-
{{ header }}
import glob
import os

from .nusimconfig import NUSimConfig

modules = glob.glob('{0:s}/*.py'.format(os.path.dirname(__file__)))
__all__ = [os.path.basename(f)[:-3] for f in modules]
