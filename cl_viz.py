#!/usr/bin/env python

import argparse
import collections
import itertools
import json
import os
import re
import subprocess
import sys

import pygraphviz as pgv

if "CODALAB_SESSION" not in os.environ:
    os.environ["CODALAB_SESSION"] = "top"

Bundle = collections.namedtuple('Bundle', 'name uuid deps')


def cl_run(cmd):
    results = None
    try:
        results = subprocess.check_output("cl "+cmd,
                                          shell=True).strip()
    except:
        pass

    return results


def parse_dep_string(d_string):
    dep = d_string.split(':')[1].strip()
    matches = re.match(r"(.*)\((.*)\)", dep)
    return matches.groups()


def deps_to_bundles(deps):
    parses = [parse_dep_string(x) for x in deps]
    bundles = [Bundle(name=x,
                      uuid=y,
                      deps=get_bundle_dependencies(y))
               for (x, y) in parses]
    return bundles


def get_bundle_dependencies(bundle_spec):
    # Note: not using `cl info -f dependencies` because that doesn't
    # include the uuids of the dependencies. So, here we parse that
    # from the `cl info` command.
    lines = cl_run("info {}".format(bundle_spec)).split('\n')
    dep_list = [x.strip() for x in
                itertools.dropwhile(lambda x: x != "dependencies:", lines)]
    return deps_to_bundles(dep_list[1:]) if len(dep_list) > 0 else []


def add_bundle_to_graph(bundle, graph, attrs, depth, maxdistance):
    uuid = bundle.uuid
    name = bundle.name
    node_name = "{}\n({})".format(name, uuid[:8])
    node_attrs = attrs['nodeattrs']
    node_attrs['label'] = node_name
    if uuid not in graph:
        graph.add_node(uuid, **node_attrs)

    if depth < maxdistance:
        for b in bundle.deps:
            add_bundle_to_graph(b, graph, attrs, depth+1, maxdistance)
            graph.add_edge(uuid, b.uuid, **attrs['edgeattrs'])


def main():
    # 
    def_graph_attrs = {'strict': True, 'directed': True, 'splines': True,
                       'size': '7.75,10.25', 'nodesep': 2.0}
    def_rootnode_attrs = {'root': True, 'color': None, 'shape': 'plaintext',
                          'fontsize': 16, 'fontcolor': 'blue'}
    def_node_attrs = {'color': None, 'shape': 'plaintext', 'fontsize': 11,
                      'fontcolor': 'blue'}
    def_edge_attrs = {'weight': 0.5}
    def_out_file = 'graph.eps'

    parser = argparse.ArgumentParser(epilog="Info on graphviz attributes:"
                                     " http://www.graphviz.org/doc/info/attrs.html")
    parser.add_argument("bundlespec",
                        help="generate dependency graph for BUNDLESPEC")
    parser.add_argument("-o", "--output",  action='append', default=[],
                        help="save rendered graph to OUTPUT [{}]"
                        " (may be used multiple times)".format(def_out_file))
    parser.add_argument("-m", "--maxdistance", type=int, default=10,
                        help="max distance between nodes in the graph [{}]"
                        " (must be >= 0)".format(10))
    parser.add_argument("--graphattrs", default=json.dumps(def_graph_attrs),
                        help="graphviz graph attributes (json format)."
                        " default='{}'".format(json.dumps(def_graph_attrs)))
    parser.add_argument("--nodeattrs", default=json.dumps(def_node_attrs),
                        help="graphviz node attributes (json format)."
                        " default='{}'".format(json.dumps(def_node_attrs)))
    parser.add_argument("--rootnodeattrs",
                        default=json.dumps(def_rootnode_attrs),
                        help="graphviz root node attributes (json format)."
                        " default='{}'".format(json.dumps(def_rootnode_attrs)))
    parser.add_argument("--edgeattrs", default=json.dumps(def_edge_attrs),
                        help="graphviz edge attributess (json format)."
                        " default='{}'".format(json.dumps(def_edge_attrs)))
    layout_choices = ['neato', 'dot', 'twopi', 'circo', 'fdp', 'nop']
    parser.add_argument("--layout", choices=layout_choices, default='circo',
                        help="graphviz layout algorithm [circo]")

    args = parser.parse_args()
    out_files = args.output if len(args.output) > 0 else [def_out_file]
    
    if args.maxdistance and args.maxdistance < 0:
        parser.error("Minimum distance is 0")

    gv_attrs = {}
    gv_attrs['graphattrs'] = json.loads(args.graphattrs)
    gv_attrs['nodeattrs'] = json.loads(args.nodeattrs)
    gv_attrs['rootnodeattrs'] = json.loads(args.rootnodeattrs)
    gv_attrs['edgeattrs'] = json.loads(args.edgeattrs)

    root = args.bundlespec
    root_uuid = cl_run("info -f uuid {}".format(root))
    if not root_uuid:
        sys.exit("try running 'cl ls' to check the bundle specification.")

    root_name = cl_run("info -f name {}".format(root))
    print("Creating graph for bundle: {}({})".format(root_name, root_uuid))

    root_deps = get_bundle_dependencies(root_uuid)
    root_bundle = Bundle(name=root_name, uuid=root_uuid, deps=root_deps)

    G = pgv.AGraph(**gv_attrs['graphattrs'])
    add_bundle_to_graph(root_bundle, G, gv_attrs, 0, args.maxdistance)

    # Modify the root node with user-specified attributes
    G.add_node(root_uuid, **gv_attrs['rootnodeattrs'])

    G.layout(prog=args.layout)

    for f in out_files:
        print("Saving graph to: {}".format(f))
        G.draw(f)

    return 0


if __name__ == "__main__":
    sys.exit(main())
