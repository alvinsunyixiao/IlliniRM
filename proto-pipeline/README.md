# How to run a model with Jupyter

## Prerequisites
* Homebrew installed python
* pip2 (included in the Homebrew installed python)

## Come to Jupyter
### Prepare the needed files
* After `git pull`ed in the `IlliniRM` directory, input `mkdir model` to creat a new directory and downlowd files in [Google Drive](https://drive.google.com/drive/u/1/folders/151dvJA-1cIoJ5kNKNFrwGojRCTCMHgle) into the just-created directory.

### Install Jupyter
* Make sure you are in the `IlliniRM` directory, then `cd proto-pipeline`.
* input `sudo pip2 install jupyter` to install jupyter.

### Run Jupyter
* Make sure you are in the `IlliniRM/proto-pipeline` directory, input `jupyter notebook`.
* A webpage will pop-up, which webpage should look like this![Jupyter_example_0](/Users/mingdama/Desktop/Screen Shot 2017-12-03 at 4.10.52 PM.png)
* Click the `grid-detect.ipynb`.
* The new webpage should look like this ![Jupyter_example_1](/Users/mingdama/Desktop/Screen Shot 2017-12-03 at 4.14.11 PM.png)
* You can see that the codes are separated into several blocks, click on one of them to select the block you want to run, in this case we choose the first block.
* Click on `Run`.
* The number after the `In` should turn into a `*`, just like: ![Jupyter_example_2](/Users/mingdama/Desktop/Screen Shot 2017-12-03 at 4.18.13 PM.png)
* The running is completed when the `*` turns back to a number,like: ![Jupyter_example_3](/Users/mingdama/Desktop/Screen Shot 2017-12-03 at 4.18.17 PM.png)
* Run the blocks one by one, take care of the bottom of each block after you run them, an error message might pop-up.
* Run through all the blocks.
* (To exit in the terminal, press `Ctrl+C`, then input  `y`)

## More link
* [Main page of Project Jupyter](http://jupyter.org/)