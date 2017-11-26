# How to Build Caffe DL Framework (For Mac User)
  
## Prerequisites 
* [Homebrew](https://brew.sh/)
* Python (Recommend to use python2 installed from [Homebrew](https://brew.sh/): `brew install python2`)

## Come to Caffe

### Dependencies

* General dependencies

```
brew install -vd snappy leveldb gflags glog szip lmdb
brew tap homebrew/science
brew install hdf5
brew install opencv --with-python --with-python3
```

* Remaining dependencies

```
sudo -H pip2 install numpy
brew install --build-from-source --with-python -vd protobuf
brew install --build-from-source -vd boost boost-python
brew install openblas    
```

### Build Caffe 

* Make sure you are in the `IlliniRM/caffe` directory.
* Then, input the following commands:

```
make all 
make pycaffe
cd python && sudo -H pip2 install -r requirements.txt
```
### Setup PYTHONPATH
* Make sure to replace `<path to IlliniRM/caffe/python>` with your **Absolute Path**
* For bash user

```
(For bash users): echo "export PYTHONPATH=<path to IlliniRM/caffe/python>:\$PYTHONPATH" >> ~/.bash_profile
```
* For zsh user

```
(For zsh users): echo "export PYTHONPATH=<path to IlliniRM/caffe/python>:\$PYTHONPATH" >> ~/.zshrc
```

### Run Digit Recognition Demo
* Download two files from the [Google Drive](https://drive.google.com/drive/u/1/folders/151dvJA-1cIoJ5kNKNFrwGojRCTCMHgle) to `training-zoo/minist/demo`.
* Run `python2 demo.py` to demo.

## References and More Links (For Windows & Linux Users)
* [Caffe's OS X Installation](http://caffe.berkeleyvision.org/install_osx.html)
* [Trained Model](https://drive.google.com/drive/u/1/folders/1Za_5X8DBD2OeAjottFdYQ94skK8arM-T)


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