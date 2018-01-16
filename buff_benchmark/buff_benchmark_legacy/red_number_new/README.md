# Buff_Benchmark

## 描述
Dilation 处理的数位训练集（未去重）

工作方式：
1. 懒得写。。大概就是用了 digit_displayer 里的类，见代码

## 依赖库
- Python Opencv
- PIL (Pillow)

## 使用方法
1. 安装依赖库。
2. python training_red_num_generator.py

## TODO
- 去重
- 再添加干扰？（目前 Alvin 的训练程序在输入模型前，已经有 preprocess 的操作了（旋转，添加噪声等）。可以考虑加其他的变换）
