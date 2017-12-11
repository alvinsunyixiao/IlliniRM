# Buff_Benchmark

## 描述
Python 2 大符模拟器。采用[辣鸡官方大符模拟器](http://bbs.robomasters.com/thread-4523-1-1.html)里的图片素材制作，老少 (Mac) 用户皆宜。未在其他平台测试过。
最新的 benchmark STATs 在当前目录的 html 文件内。

工作方式：
1. 随机读取相应数字素材，并显示到屏幕上。
2. 被测试者（模型）可以用 Webcam 对显示屏识别数字，并与 Benchmark 程序输出的正确序列进行比对。
3. 进行 n 轮测试后，benchmark 返回正确率和错题集。

## 依赖库
- Matplotlib
- PIL (Pillow)

## 使用方法
1. 安装依赖库。
2. 调整程序开头的参数，比如分辨率（推荐值：1920*1080）等等
3. python benchmark.py

## 使用 socket 来提交结果
1. 修改 buff_benchmark_comm.py 的头部 constants，注意区分内外部地址
2. 修改 benchmark.py 头部，将 \_USE\_SOCKET 设为 True
3. 在 detect 程序里面 import buff_benchmark_comm
4. client = buff_benchmark_comm.client()
5. client.update([1, 2, 3, 4, 5, 6, 7, 8, 9])

## TODO
- 扩大数据集（自己手写？）
- 根据规则调整程序，使时间间隔、图片和黑条等参数更贴近实际情况
- 返回错题集
- Socket 客户端目前是用的很简单的固定 tolerance 的方法来检测新回合。update 可能会更好
- (Optional) 添加干扰（包括但不限于旋转，噪声等等）
