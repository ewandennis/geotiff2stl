import numpy as np
import skimage as ski
from stl import mesh

import sys

HSCALE = 50
ZSCALE = 3
BOXHEIGHT = 1000

def noop(*args):
    pass

debug = noop #print

def topwall(verts, tris, ptsperrow, wallbottom):
    vertspersurface = len(verts)/2
    for idx in range(ptsperrow-1):
        pt0idx = idx
        pt1idx = vertspersurface + idx
        tri0 = [pt0idx, pt0idx+1, pt1idx+1] # upper right tri
        tri1 = [pt0idx, pt1idx+1, pt1idx]   # lower left tri
        tris.append(tri0)
        tris.append(tri1)

def btmwall(verts, tris, ptsperrow, wallbottom):
    vertspersurface = len(verts)/2
    lastrowvertidx = vertspersurface - ptsperrow
    for idx in range(ptsperrow-1):
        pt0idx = lastrowvertidx + idx
        pt1idx = pt0idx + vertspersurface
        tri0 = [pt0idx, pt1idx+1, pt0idx+1] # upper right tri
        tri1 = [pt0idx, pt1idx, pt1idx+1]   # lower left tri
        tris.append(tri0)
        tris.append(tri1)

def leftwall(verts, tris, rows, ptsperrow, wallbottom):
    vertspersurface = len(verts)/2
    for idx in range(rows-1):
        pt0idx = idx * ptsperrow
        pt1idx = pt0idx + vertspersurface
        tri0 = [pt0idx, pt1idx+ptsperrow, pt0idx+ptsperrow] # upper right tri
        tri1 = [pt0idx, pt1idx, pt1idx+ptsperrow,]   # lower left tri
        tris.append(tri0)
        tris.append(tri1)

def rightwall(verts, tris, rows, ptsperrow, wallbottom):
    vertspersurface = len(verts)/2
    for idx in range(rows-1):
        pt0idx = (idx+1) * ptsperrow - 1
        pt1idx = pt0idx + vertspersurface
        tri0 = [pt0idx, pt0idx+ptsperrow, pt1idx+ptsperrow] # upper right tri
        tri1 = [pt0idx, pt1idx+ptsperrow, pt1idx]   # lower left tri
        tris.append(tri0)
        tris.append(tri1)

def base(verts, tris, rows, ptsperrow, wallbottom):
    # copy terrain verts and flatten to z=wallbottom
    nterrainverts = rows * ptsperrow
    basevertidx = len(verts)
    verts.extend(verts[:])
    for idx in range(nterrainverts):
        verts[basevertidx + idx] = verts[basevertidx + idx][:]
        verts[basevertidx + idx][2] = wallbottom

    # copy terrain tris and flip to point out
    nterraintris = (rows-1) * (ptsperrow-1) * 2
    basetriidx = len(tris)
    tris.extend(tris[:nterraintris])
    for idx in range(nterraintris):
        tris[basetriidx+idx] = [
            tris[basetriidx+idx][2] + basevertidx,
            tris[basetriidx+idx][1] + basevertidx,
            tris[basetriidx+idx][0] + basevertidx
        ]

def main(inpath, outpath, xscale, yscale, zscale, boxheight):
    # load geotiff
    img = ski.io.imread(inpath)

    # assert: need >1 row and >1 col
    assert(img.shape[0] > 1 and img.shape[1] > 1)

    debug('img shape = ', img.shape)

    # channel 0 only
    channel0 = img
    if len(img.shape) == 3:
        channel0 = img[...,0]

    rows, ptsperrow = channel0.shape
    debug('input shape = ', channel0.shape)
    debug(channel0)

    # build verts from pixels
    verts = [
        [x * xscale, (1. - y) * yscale, channel0[y, x] * zscale]
        for y in range(rows)
        for x in range(ptsperrow)
    ]
    lowest=min(verts, key=lambda v: v[2])
    wallbottom = lowest[2] - boxheight

    # build tri mesh from verts
    tris = []
    for rowidx in range(rows-1):
        for colidx in range(ptsperrow-1):
            # row of tris
            pt0idx = rowidx * ptsperrow + colidx
            pt1idx = pt0idx + ptsperrow
            tri0 = [pt0idx, pt1idx+1, pt0idx+1] # upper right tri
            tri1 = [pt0idx, pt1idx, pt1idx+1]   # lower left tri
            tris.append(tri0)
            tris.append(tri1)

    base(verts, tris, rows, ptsperrow, wallbottom)

    topwall(verts, tris, ptsperrow, wallbottom)
    btmwall(verts, tris, ptsperrow, wallbottom)
    leftwall(verts, tris, rows, ptsperrow, wallbottom)
    rightwall(verts, tris, rows, ptsperrow, wallbottom)

    verts = np.array(verts)
    tris = np.array(tris, dtype=np.uint32)

    debug('verts shape = ', verts.shape)

    debug('tris shape = ', tris.shape)
    debug(tris)

    writeme = mesh.Mesh(np.zeros(tris.shape[0], dtype=mesh.Mesh.dtype))
    for triidx, face in enumerate(tris):
        for vertidx in range(3):
            writeme.vectors[triidx][vertidx] = verts[face[vertidx]]

    writeme.save(outpath)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(
            prog='tiff2stl',
            description='convert GeoTIFF files into equivalent STL manifold meshes ready for printing'
    )
    parser.add_argument('input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-xs', '--xscale', type=float, default=HSCALE)
    parser.add_argument('-ys', '--yscale', type=float, default=HSCALE)
    parser.add_argument('-zs', '--zscale', type=float, default=ZSCALE)
    parser.add_argument('-bh', '--boxheight', type=float, default=BOXHEIGHT)
    args = parser.parse_args()
    if not args.output:
        args.output = args.input + '.stl'
    print('{} -> {}'.format(args.input, args.output))
    if args.verbose:
        debug = print

    debug('scale = (%0.2f, %0.2f, %0.2f)' % (args.xscale, args.yscale, args.zscale))
    debug('box height = %0.2f' % args.boxheight)

    main(args.input, args.output, args.xscale, args.yscale, args.zscale, args.boxheight)

