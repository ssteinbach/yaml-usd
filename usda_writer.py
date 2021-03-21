#!/usr/bin/env python

# python
import argparse
import os

# local
import tilt_extract

""" Convert YAML to/from USD """


def parse_args():
    """ parse arguments out of sys.argv """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d",
        "--dryrun",
        action="store_true",
        default=False,
        help="dryrun mode - print what *would* be done"
    )
    parser.add_argument(
        'filepath',
        type=str,
        nargs='+',
        help='YAML files to parse'
    )
    return parser.parse_args()


# USDA TEMPLATE
FILE_TEMPLATE = """#usda 1.0
(
    endFrame = 1
    startFrame = 1
)

def Scope "World" (
    customData = {{
        bool zUp = 0
    }}
)
{{
    {body}
}}
"""

CURVE_TEMPLATE = """
    def BasisCurves "{name}"
    {{
        uniform token basis = "bezier"
        int[] curveVertexCounts = [{nverts}]
        Vec3f[] extent = [{min_e}, {max_e}]
        uniform token orientation = "rightHanded"
        PointFloat[] points = {points}
        ColorFloat[] primvars:displayColor = [{color}]
        uniform token type = "cubic"
        float[] widths = [{width}]
        custom Matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) )
        uniform token[] xformOpOrder = ["xformOp:transform"]
    }}"""


def to_usda(tb_data):
    body = ""

    for i, stroke in enumerate(tb_data['strokes']):
        cp_positions = [
            tuple(cp['position']) for cp in stroke['control_points']
        ]
        stroke_data = {
            'name': 'tiltbrush_stroke_{}'.format(i),
            'width': stroke['brush_size'],
            'color': tuple(stroke['brush_color'][0:3]),
            'nverts': len(cp_positions),
            'points': cp_positions,
        }
        min_p = list(cp_positions[0])
        max_p = list(cp_positions[1])
        for p in cp_positions[1:]:
            for dim in range(3):
                min_p[dim] = min(min_p[dim], p[dim])
                max_p[dim] = max(max_p[dim], p[dim])
        stroke_data['min_e'] = tuple(min_p)
        stroke_data['max_e'] = tuple(max_p)

        body += CURVE_TEMPLATE.format(**stroke_data)

    return FILE_TEMPLATE.format(body=body)


def main():
    """main function for module"""
    args = parse_args()

    for fp in args.filepath:
        outpath = "{}.usda".format(os.path.basename(fp))
        print("Attempting to write: {}".format(outpath))
        with open(outpath, 'w') as fo:
            fo.write(to_usda(tilt_extract.extract(fp)))
            print("Success.")


if __name__ == '__main__':
    main()
