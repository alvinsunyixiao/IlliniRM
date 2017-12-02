# How To Train LeNet with MNIST Dataset

This directory includes official LeNet CNN structure file `lenet_train_test.prototxt.example` as well as the default training configuration `lenet_solver.prototxt.example`. Follow this instruction to start training your first caffe model and play around with different training configurations.

**Important: Do NOT modify any file that ends with `.example` !**

## Prerequisite

[caffe](https://github.com/alvinsunyixiao/IlliniRM/tree/master/caffe)

## Setup & Test Run

* Make sure to `cd` into `IlliniRM/training-zoo/mnist` directory
* Run the following commands:

```sh
./data/get_mnist.sh       	# download the official data package
./create_mnist.sh         	# convert the compressed data into lmdb database
``` 

* You should see the generated `lenet_train_test.prototxt` & `lenet_solver.prototxt` in your directory

## Start a Training Session
* Run the following script:

```sh
./train_lenet.sh
```
* Trained model and optimizer state will be stored in the `./snapshot` directory.

## Play Around With Customized Configuration

* Modify `lenet_train_test.prototxt` to
	* Change default LeNet CNN structure
	* Change data augmentation parameters
* Modify `lenet_solver.prototxt` to cusomize:
	* base learning rate
	* learning rate decay policy
	* training iterations
	* optimizer type
	* etc...