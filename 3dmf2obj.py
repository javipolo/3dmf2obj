#!/usr/bin/env python3
"""Convert a QuickDraw3D text Metafile (.3dmf) to Wavefront OBJ + MTL.

Handles the LimeLight cave-survey subset: TriMesh geometry, per-mesh
DiffuseColor, and segment names from URLElement/CString. Mac Roman / CR
line endings are handled.

Copyright (C) 2026 Javi Polo

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version. This program is distributed WITHOUT ANY WARRANTY. See
the GNU General Public License (LICENSE file) for more details.
"""
import argparse
import os
import re
import sys

__version__ = "1.0.0"


def convert(src, out_obj, quiet=False):
    """Parse the .3dmf at *src* and write OBJ to *out_obj* (+ sibling .mtl)."""
    # QD3D files use CR line endings and Mac Roman encoding.
    with open(src, 'rb') as f:
        raw = f.read()
    text = raw.replace(b'\r\n', b'\n').replace(b'\r', b'\n').decode('mac_roman')
    lines = text.split('\n')

    meshes = []  # list of dict: name, color, tris, verts
    i = 0
    n = len(lines)
    hdr_re = re.compile(r'Trimesh\s*\(\s*(\d+)\s+\d+\s+\d+\s+\d+\s+(\d+)\s+\d+')
    col_re = re.compile(r'DiffuseColor\s*\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)')
    name_re = re.compile(r'"([^"]*)"')

    while i < n:
        m = hdr_re.search(lines[i])
        if not m:
            i += 1
            continue
        ntri, npts = int(m.group(1)), int(m.group(2))
        i += 1
        tris = []
        for _ in range(ntri):
            a, b, c = lines[i].split()[:3]
            tris.append((int(a), int(b), int(c)))
            i += 1
        verts = []
        for _ in range(npts):
            x, y, z = lines[i].split()[:3]
            verts.append((float(x), float(y), float(z)))
            i += 1
        # Scan forward for this mesh's color and name (before next Trimesh).
        color = (0.8, 0.8, 0.8)
        name = f'mesh_{len(meshes)}'
        j = i
        while j < n and not hdr_re.search(lines[j]):
            cm = col_re.search(lines[j])
            if cm:
                color = tuple(float(cm.group(k)) for k in (1, 2, 3))
            if 'CString' in lines[j]:
                # name is on the following quoted line(s)
                for k in range(j, min(j + 3, n)):
                    nm = name_re.search(lines[k])
                    if nm and nm.group(1):
                        name = nm.group(1)
                        break
            j += 1
        meshes.append(dict(name=name, color=color, tris=tris, verts=verts))

    if not meshes:
        raise ValueError('no TriMesh geometry found (is this a QuickDraw3D text .3dmf?)')

    # Write OBJ + MTL
    base = os.path.splitext(os.path.basename(out_obj))[0]
    mtl_path = os.path.join(os.path.dirname(out_obj) or '.', base + '.mtl')
    with open(out_obj, 'w') as fo, open(mtl_path, 'w') as fm:
        fo.write(f'# Converted from {os.path.basename(src)}\n')
        fo.write(f'mtllib {base}.mtl\n')
        voff = 0
        for idx, me in enumerate(meshes):
            safe = re.sub(r'[^\w.-]', '_', me['name']) or f'mesh_{idx}'
            mat = f'mat_{idx}'
            r, g, b = me['color']
            fm.write(f'newmtl {mat}\nKd {r:.4f} {g:.4f} {b:.4f}\nKa {r*0.3:.4f} {g*0.3:.4f} {b*0.3:.4f}\nd 1.0\nillum 1\n\n')
            fo.write(f'g {safe}\nusemtl {mat}\n')
            for x, y, z in me['verts']:
                fo.write(f'v {x} {y} {z}\n')
            for a, b2, c in me['tris']:
                fo.write(f'f {a+1+voff} {b2+1+voff} {c+1+voff}\n')
            voff += len(me['verts'])

    tot_v = sum(len(m['verts']) for m in meshes)
    tot_f = sum(len(m['tris']) for m in meshes)
    if not quiet:
        print(f'{len(meshes)} meshes, {tot_v} verts, {tot_f} faces')
        print(f'wrote {out_obj}')
        print(f'wrote {mtl_path}')
    return out_obj, mtl_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog='3dmf2obj',
        description='Convert a QuickDraw3D text Metafile (.3dmf) to Wavefront OBJ + MTL.',
        epilog='Example: 3dmf2obj.py cave.3dmf cave.obj',
    )
    parser.add_argument('input', help='source .3dmf file')
    parser.add_argument(
        'output',
        nargs='?',
        help='destination .obj file (default: input name with .obj extension)',
    )
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress progress output')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not os.path.isfile(args.input):
        sys.exit(f'error: input file not found: {args.input}')

    out_obj = args.output or os.path.splitext(args.input)[0] + '.obj'

    try:
        convert(args.input, out_obj, quiet=args.quiet)
    except (ValueError, OSError, UnicodeDecodeError) as e:
        sys.exit(f'error: {e}')


if __name__ == '__main__':
    main()
