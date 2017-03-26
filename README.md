# cl_viz
Codalab dependency graph visualization

This utility will produce a graphical representation of dependency graphs in
codalab.

For example:

``` bash
cl run "echo a" -n a
cl run :a "echo b" -n b
cl run :b "echo c" -n c
./cl_viz.py -o example.png c
```

This `./cl_viz.py` command will put the dependency graph image into `example.png`:
![Example cl_viz.py output](/example.png?raw=true "example.png")


## Requirements

You need to have access to a codalab server (e.g. http://www.codalab.org) and the
[codalab cli tools](https://github.com/codalab/codalab-cli) installed.

To install the codalab cli tools:
```
pip install codalab-cli
```
You will also need the [pygraphviz](https://pygraphviz.github.io/) package.

```
pip install pygraphviz
```
And finally, pygraphviz requires that [graphviz](http://www.graphviz.org/) is installed.
On Mac OS, you should be able to install using `brew install graphviz`.

## Installation

Once you have the requirements above installed, just download `cl_viz.py` from this repo.

## Usage:
```
usage: cl_viz.py [-h] [-o OUTPUT] [-m MAXDISTANCE] [--graphattrs GRAPHATTRS]
                 [--nodeattrs NODEATTRS] [--rootnodeattrs ROOTNODEATTRS]
                 [--edgeattrs EDGEATTRS]
                 [--layout {neato,dot,twopi,circo,fdp,nop}]
                 bundlespec

positional arguments:
  bundlespec            generate dependency graph for BUNDLESPEC

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        save rendered graph to OUTPUT [graph.eps] (may be used
                        multiple times)
  -m MAXDISTANCE, --maxdistance MAXDISTANCE
                        max distance between nodes in the graph [10] (must be
                        >= 0)
  --graphattrs GRAPHATTRS
                        graphviz graph attributes (json format).
                        default='{"directed": true, "strict": true, "nodesep":
                        2.0, "splines": true, "size": "7.75,10.25"}'
  --nodeattrs NODEATTRS
                        graphviz node attributes (json format).
                        default='{"color": null, "fontcolor": "blue", "shape":
                        "plaintext", "fontsize": 11}'
  --rootnodeattrs ROOTNODEATTRS
                        graphviz root node attributes (json format).
                        default='{"color": null, "fontsize": 16, "shape":
                        "plaintext", "root": true, "fontcolor": "blue"}'
  --edgeattrs EDGEATTRS
                        graphviz edge attributess (json format).
                        default='{"weight": 0.5}'
  --layout {neato,dot,twopi,circo,fdp,nop}
                        graphviz layout algorithm [circo]

Info on graphviz attributes: http://www.graphviz.org/doc/info/attrs.html
```
