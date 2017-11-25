#!/usr/bin/env sh
set -e

../../caffe/build/tools/caffe train --solver=./lenet_solver.prototxt $@
