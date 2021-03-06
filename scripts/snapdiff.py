#!/usr/bin/env python
##########################################################################
#
# Copyright 2011 Jose Fonseca
# Copyright 2008-2009 VMware, Inc.
# All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
##########################################################################/


'''Snapshot (image) comparison script.
'''


import sys
import os.path
import optparse
import math
import operator

from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance


thumb_size = 320, 320


class Comparer:
    '''Image comparer.'''

    def __init__(self, ref_image, src_image, alpha = False):
        if isinstance(ref_image, basestring):
            self.ref_im = Image.open(ref_image)
        else:
            self.ref_im = ref_image

        if isinstance(src_image, basestring):
            self.src_im = Image.open(src_image)
        else:
            self.src_im = src_image

        # Ignore
        if not alpha:
            self.ref_im = self.ref_im.convert('RGB')
            self.src_im = self.src_im.convert('RGB')

        self.diff = ImageChops.difference(self.src_im, self.ref_im)

    def write_diff(self, diff_image, fuzz = 0.05):
        # make a difference image similar to ImageMagick's compare utility
        mask = ImageEnhance.Brightness(self.diff).enhance(1.0/fuzz)
        mask = mask.convert('L')

        lowlight = Image.new('RGB', self.src_im.size, (0xff, 0xff, 0xff))
        highlight = Image.new('RGB', self.src_im.size, (0xf1, 0x00, 0x1e))
        diff_im = Image.composite(highlight, lowlight, mask)

        diff_im = Image.blend(self.src_im, diff_im, 0xcc/255.0)
        diff_im.save(diff_image)

    def precision(self):
        # See also http://effbot.org/zone/pil-comparing-images.htm
        h = self.diff.histogram()
        square_error = 0
        for i in range(1, 256):
            square_error += sum(h[i : 3*256: 256])*i*i
        rel_error = float(square_error*2 + 1) / float(self.diff.size[0]*self.diff.size[1]*3*255*255*2)
        bits = -math.log(rel_error)/math.log(2.0)
        return bits

    def ae(self):
        # Compute absolute error
        # TODO: this is approximate due to the grayscale conversion
        h = self.diff.convert('L').histogram()
        ae = sum(h[int(255 * fuzz) + 1 : 256])
        return ae


def surface(html, image):
    if True:
        name, ext = os.path.splitext(image)
        thumb = name + '.thumb' + ext
        if os.path.exists(image) \
           and (not os.path.exists(thumb) \
                or os.path.getmtime(thumb) < os.path.getmtime(image)):
            im = Image.open(image)
            im.thumbnail(thumb_size)
            im.save(thumb)
    else:
        thumb = image
    html.write('        <td><a href="%s"><img src="%s"/></a></td>\n' % (image, thumb))


def is_image(path):
    return \
        path.endswith('.png') \
        and not path.endswith('.diff.png') \
        and not path.endswith('.thumb.png')


def find_images(prefix):
    prefix = os.path.abspath(prefix)
    if os.path.isdir(prefix):
        prefix_dir = prefix
    else:
        prefix_dir = os.path.dirname(prefix)

    images = []
    for dirname, dirnames, filenames in os.walk(prefix_dir, followlinks=True):
        for filename in filenames:
            filepath = os.path.join(dirname, filename)
            if filepath.startswith(prefix) and is_image(filepath):
                images.append(filepath[len(prefix):])

    return images


def main():
    global options

    optparser = optparse.OptionParser(
        usage="\n\t%prog [options] <ref_prefix> <src_prefix>")
    optparser.add_option(
        '-o', '--output', metavar='FILE',
        type="string", dest="output", default='index.html',
        help="output filename [default: %default]")
    optparser.add_option(
        '-f', '--fuzz',
        type="float", dest="fuzz", default=0.05,
        help="fuzz ratio [default: %default]")
    optparser.add_option(
        '--overwrite',
        action="store_true", dest="overwrite", default=False,
        help="overwrite")

    (options, args) = optparser.parse_args(sys.argv[1:])

    if len(args) != 2:
        optparser.error('incorrect number of arguments')

    ref_prefix = args[0]
    src_prefix = args[1]

    ref_images = find_images(ref_prefix)
    src_images = find_images(src_prefix)
    images = list(set(ref_images).intersection(set(src_images)))
    images.sort()

    if options.output:
        html = open(options.output, 'wt')
    else:
        html = sys.stdout
    html.write('<html>\n')
    html.write('  <body>\n')
    html.write('    <table border="1">\n')
    html.write('      <tr><th>%s</th><th>%s</th><th>&Delta;</th></tr>\n' % (ref_prefix, src_prefix))
    for image in images:
        ref_image = ref_prefix + image
        src_image = src_prefix + image
        root, ext = os.path.splitext(src_image)
        delta_image = "%s.diff.png" % (root, )
        if os.path.exists(ref_image) and os.path.exists(src_image):
            if options.overwrite \
               or not os.path.exists(delta_image) \
               or (os.path.getmtime(delta_image) < os.path.getmtime(ref_image) \
                   and os.path.getmtime(delta_image) < os.path.getmtime(src_image)):

                comparer = Comparer(ref_image, src_image)
                comparer.write_diff(delta_image, fuzz=options.fuzz)

            html.write('      <tr>\n')
            surface(html, ref_image)
            surface(html, src_image)
            surface(html, delta_image)
            html.write('      </tr>\n')
            html.flush()
    html.write('    </table>\n')
    html.write('  </body>\n')
    html.write('</html>\n')


if __name__ == '__main__':
    main()
