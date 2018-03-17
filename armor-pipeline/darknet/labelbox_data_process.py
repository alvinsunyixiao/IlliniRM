import json
import sys
import os
import numpy as np
from tqdm import tqdm
import requests

'''
#@TODO:
    1. Add repetitive data bounding box averaging
    2. Split a subset of data as validation set
    3. Now it only extracts red armor. Add a function that extract them from the same frame
'''

downloaded_json_file = "200.json"
image_data_folder = "img_data"

if not os.path.exists(image_data_folder):
    os.makedirs(image_data_folder)

class piece_of_training_data(object):
    __slots__ = ("image_path", "label")


'''
    @Param:
        1. a set of Labelbox styled coordinates e.g. data[0]["Label"]["Red Armor"][0]
    @return:
        1. yolo styled propotional coordinates (class_num, center_x, center_y, width, height)
'''
def labelbox_coord_2_yolo(coord, class_name):
    class_type = 0
    if class_name == "Blue Armor":
        class_type = 1
    image_height = 1080
    image_width = 1920
    dh = 1.0 / image_height
    dw = 1.0 / image_width
    leftmost_x = min(coord, key = lambda entry: entry['x'])['x']
    rightmost_x = max(coord, key = lambda entry: entry['x'])['x']
    lower_y = min(coord, key = lambda entry: entry['y'])['y']
    upper_y = max(coord, key = lambda entry: entry['y'])['y']
    center_x = (leftmost_x + rightmost_x) / 2.0 * dw
    center_y = (1 - (lower_y + upper_y) / 2.0 * dh)
    width = (rightmost_x - leftmost_x) * dw
    height = (upper_y - lower_y) * dh
    return (class_type, center_x, center_y, width, height)

'''
    @Param: path to a json file
    @return:
        1. url path to the images
        2. corresponding label data to each url path
'''
def parse_data(json_file_path):
    json_data = json.load(open(json_file_path))
    row_num = len(json_data)
    ret_samples = []
    visited_dict = {} #we shouldn't be doing this
    for i in range(row_num):
        cur_piece = piece_of_training_data()
        cur_piece.image_path = json_data[i]["Labeled Data"]
        try:
            if visited_dict[cur_piece.image_path]:
                continue #visited
        except KeyError:
            #unvisited
            visited_dict[cur_piece.image_path] = True
        cur_piece.label = []
        for bounding_rect in json_data[i]["Label"]["Red Armor"]:
            cur_piece.label.append(labelbox_coord_2_yolo(bounding_rect, "Red Armor"))
        ret_samples.append(cur_piece)
    return ret_samples

def download_all_images(training_samples, save_path):
    print("Downloading images...")
    for sample in tqdm(training_samples):
        real_name = sample.image_path.split("/")[-1]
        path_of_this_image = save_path + real_name
        if os.path.isfile(path_of_this_image):
            #we have downloaded this one!
            continue
        r = requests.get(sample.image_path)
        with open(path_of_this_image, "wb") as f:
            f.write(r.content)

def make_individual_label(samples_list, img_path):
    for sample in samples_list:
        txt_path = img_path + sample.image_path.split("/")[-1].split(".")[0] +".txt"
        with open(txt_path, "w") as f:
            for label in sample.label:
                for item in label:
                    f.write(str(item))
                    f.write(" ")
                f.write("\n") #or \r\n ?

def make_training_list(training_set, img_path):
    data_path = os.getcwd() + "/" + img_path
    with open("training_list.txt", "w") as f:
        for sample in training_set:
            img_name = sample.image_path.split("/")[-1]
            f.write(data_path + img_name)
            f.write("\n")

def main(json_path, data_path):
    training_set = parse_data(json_path)
    download_all_images(training_set, data_path + "/")
    make_individual_label(training_set, data_path + "/")
    make_training_list(training_set, data_path + "/")

if __name__ == '__main__':
    main(downloaded_json_file, image_data_folder)
