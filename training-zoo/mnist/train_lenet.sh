#!/usr/bin/env sh
set -e

export PYTHONPATH=$(pwd -P)/pylayer:$PYTHONPATH
mkdir -p snapshot
../../caffe/build/tools/caffe train --solver=./lenet_solver.prototxt 
