#!/usr/bin/env python

# python
import argparse
import os

import yaml

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
        custom Matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1) ) # noqa E501
        uniform token[] xformOpOrder = ["xformOp:transform"]
    }}"""


BASIC_TYPE_MAP = {
    int: "int",
    float: "float",
    str: "token",
}
INT_TEMPLATE = "int {key} = {val}"
FLOAT_TEMPLATE = "float {key} = {val}"
STRING_TEMPLATE = 'token {key} = "{val}"'
LIST_TEMPLATE = '{ltype}[] {key} = [{values}]'
SCOPE_TEMPLATE = """def Scope "{name}"
{{
body
}}"""


# gets filled in by usda_dispatch_for decorator
TO_USDA_DISPATCH_TABLE = {}


def usda_dispatch_for(typeobj):
    def wrapped_for_type(fn):
        TO_USDA_DISPATCH_TABLE[typeobj] = fn
        return fn
    return wrapped_for_type


@usda_dispatch_for(int)
def write_int(key, val):
    return INT_TEMPLATE.format(key=key, val=val)


@usda_dispatch_for(float)
def write_float(key, val):
    return FLOAT_TEMPLATE.format(key=key, val=val)


@usda_dispatch_for(str)
def write_string(key, val):
    return STRING_TEMPLATE.format(key=key, val=val)


@usda_dispatch_for(type([]))
def write_list(key, val):
    if val:
        list_type = type(val[0])
    else:
        list_type = int

    list_type_key = BASIC_TYPE_MAP[list_type]

    def string_handler(val):
        return '"{}"'.format(val)

    if list_type == str:
        list_type = string_handler

    return LIST_TEMPLATE.format(
        ltype=list_type_key,
        key=key,
        values=",".join(list_type(v) for v in val)
    )


@usda_dispatch_for(type({}))
def write_scope(key, val):
    return SCOPE_TEMPLATE.format(name=key, body=write_map(val))


def write_map(val):
    body = ""

    for key, val in val.items():
        val_type = type(val)
        try:
            body += TO_USDA_DISPATCH_TABLE[val_type](key, val)
        except KeyError:
            raise ValueError(
                "'{}' data is unsupported.  Key: {}, Value: {}.  Supported"
                " types are: {}".format(
                    val_type,
                    key,
                    val,
                    list(TO_USDA_DISPATCH_TABLE.keys())
                )
            )

    return body


def to_usda(tb_data):
    try:
        tb_data.items()
    except AttributeError:
        raise ValueError(
            "Got '{}', expected dictionary like object.  Object: {}".format(
                type(tb_data),
                tb_data
            )
        )

    return FILE_TEMPLATE.format(body=write_map(tb_data))


def main():
    """main function for module"""
    args = parse_args()

    for fp in args.filepath:
        outpath = "{}.usda".format(os.path.basename(fp))
        print("Attempting to write: {}".format(outpath))
        with open(outpath, 'w') as fo:
            fo.write(to_usda(os.path.basename(fp), yaml.load(fp)))
            print("Success.")


if __name__ == '__main__':
    main()
