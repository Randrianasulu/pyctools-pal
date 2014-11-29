#!/usr/bin/env python
#  Pyctools-pal - PAL coding and decoding with Pyctools.
#  http://github.com/jim-easterbrook/pyctools-pal
#  Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

"""Transform PAL decoder components.

"""

__all__ = ['FTFilterUV', 'PostFilterUV']

import math

import numpy

from pyctools.components.interp.filtergenerator import FilterGeneratorCore
from pyctools.components.interp.resize import Resize
from pyctools.core.base import Transformer
from pyctools.core.config import ConfigEnum, ConfigFloat, ConfigInt
from pyctools.core.types import pt_complex
from .transformcore import transform_filter

class FTFilterUV(Transformer):
    def initialise(self):
        self.config['xtile'] = ConfigInt(min_value=0, dynamic=True)
        self.config['ytile'] = ConfigInt(min_value=0, dynamic=True)
        self.config['mode'] = ConfigEnum(
            choices=('limit', 'thresh'), dynamic=True)
        self.config['threshold'] = ConfigFloat(min_value=0.0, dynamic=True)

    def transform(self, in_frame, out_frame):
        self.update_config()
        x_tile = self.config['xtile']
        y_tile = self.config['ytile']
        mode = self.config['mode']
        threshold = self.config['threshold']
        in_data = in_frame.as_numpy(dtype=pt_complex)
        x_len = in_data.shape[1]
        y_len = in_data.shape[0]
        x_blk = x_len // x_tile
        y_blk = y_len // y_tile
        in_data = in_data.reshape(y_blk, y_tile, x_blk, x_tile)
        out_data = numpy.zeros(in_data.shape, dtype=pt_complex)
        transform_filter(out_data, in_data, ord(mode[0]), threshold)
        out_data = out_data.reshape(y_len, x_len, 1)
        audit = out_frame.metadata.get('audit')
        audit += 'data = TransformFilter(data)\n'
        audit += '    tile size: %d x %d\n' % (y_tile, x_tile)
        audit += '    mode: %s, threshold: %g\n' % (mode, threshold)
        out_frame.metadata.set('audit', audit)
        out_frame.data = out_data
        return True


def PostFilterUV():
    resize = Resize()
    resize.filter(FilterGeneratorCore(x_ap=16, x_cut=25))
    return resize