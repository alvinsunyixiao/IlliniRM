# How to train built model (For Mac User)

  Let's use Alvin's model as example.
  
## Prerequisites 
* Homebrew (If you don't have it, just follow the instruction on [Homebrew's webpage](https://brew.sh/))
* Python (If you don't have it, install the homebrew first, then input `brew install python2 python3` in your terminal)

## Come to Caffe

### Installation

* General dependencies
	* Assume you have already installed brew, input the following commands in your terminal:

```
brew install -vd snappy leveldb gflags glog szip lmdb
brew tap homebrew/science
brew install hdf5
brew install opencv --with-python --with-python3
```
* Remaining dependencies
	* still in the terminal, input:

```
sudo pip2 install numpy
brew install --build-from-source --with-python -vd protobuf
brew install --build-from-source -vd boost boost-python
brew install openblas    
```

### Checking and Setting up 

* Make sure you are in the `caffe` directory.
* Then, input the following commands:

```
make all 
make pycaffe
export  <pythonpass>
```

### Application
* Download two files from the [Google Drive](https://github.com/alvinsunyixiao/IlliniRM/tree/master/training-zoo/mnist/demo) to `training-zoo/minist/demo`.
* Input `python2 demo.py` to demo.

## References and more Links
* [Caffe's OS X Installation](http://caffe.berkeleyvision.org/install_osx.html)
* [Alvin's model](https://github.com/alvinsunyixiao/IlliniRM)


---  
---  
---
---
___

# The official README.md (provided by Caffe)
---
# Caffe

[![Build Status](https://travis-ci.org/BVLC/caffe.svg?branch=master)](https://travis-ci.org/BVLC/caffe)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](LICENSE)

Caffe is a deep learning framework made with expression, speed, and modularity in mind.
It is developed by Berkeley AI Research ([BAIR](http://bair.berkeley.edu))/The Berkeley Vision and Learning Center (BVLC) and community contributors.

Check out the [project site](http://caffe.berkeleyvision.org) for all the details like

- [DIY Deep Learning for Vision with Caffe](https://docs.google.com/presentation/d/1UeKXVgRvvxg9OUdh_UiC5G71UMscNPlvArsWER41PsU/edit#slide=id.p)
- [Tutorial Documentation](http://caffe.berkeleyvision.org/tutorial/)
- [BAIR reference models](http://caffe.berkeleyvision.org/model_zoo.html) and the [community model zoo](https://github.com/BVLC/caffe/wiki/Model-Zoo)
- [Installation instructions](http://caffe.berkeleyvision.org/installation.html)

and step-by-step examples.

## Custom distributions

 - [Intel Caffe](https://github.com/BVLC/caffe/tree/intel) (Optimized for CPU and support for multi-node), in particular Xeon processors (HSW, BDW, SKX, Xeon Phi).
- [OpenCL Caffe](https://github.com/BVLC/caffe/tree/opencl) e.g. for AMD or Intel devices.
- [Windows Caffe](https://github.com/BVLC/caffe/tree/windows)

## Community

[![Join the chat at https://gitter.im/BVLC/caffe](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/BVLC/caffe?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Please join the [caffe-users group](https://groups.google.com/forum/#!forum/caffe-users) or [gitter chat](https://gitter.im/BVLC/caffe) to ask questions and talk about methods and models.
Framework development discussions and thorough bug reports are collected on [Issues](https://github.com/BVLC/caffe/issues).

Happy brewing!

## License and Citation

Caffe is released under the [BSD 2-Clause license](https://github.com/BVLC/caffe/blob/master/LICENSE).
The BAIR/BVLC reference models are released for unrestricted use.

Please cite Caffe in your publications if it helps your research:

    @article{jia2014caffe,
      Author = {Jia, Yangqing and Shelhamer, Evan and Donahue, Jeff and Karayev, Sergey and Long, Jonathan and Girshick, Ross and Guadarrama, Sergio and Darrell, Trevor},
      Journal = {arXiv preprint arXiv:1408.5093},
      Title = {Caffe: Convolutional Architecture for Fast Feature Embedding},
      Year = {2014}
    }