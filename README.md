# TimeConsumptionVisualizer
 A pyqt-based gui for visualizing time consumption of your code.

## 1. Usage

### 1.1 prerequisites 

```bash
pip install -r requirements.txt
```

Log your program's time consumption as the following format (.csv with delimiter ","):

| timestamp | function                                        | elapsed_time(ms) |
| --------- | ----------------------------------------------- | ---------------- |
| 270909067 | ORBextractor_ExtractORB_ComputePyramid          | 0.921355         |
| 270909075 | ORBextractor_ExtractORB_ComputeKeyPointsOctTree | 7.348959         |
| 270909081 | ORBextractor_ExtractORB_computeDescriptors      | 6.548437         |
| 270909081 | Frame_Frame_ExtractORB                          | 15.588542        |
| 270909082 | Tracking_GrabImageMonocular_Frame               | 16.239584        |

Notice: the function name should be: file name_parent module_curent module

### 1.2 run python scripts

```bash
cd ./scripts
python show_gui.py PATH/TO/TIME_LOG_DATA
```

or set variable PATH in config.py, then

```
python show_gui.py
```

![image-20230207123932063](https://p.ipic.vip/kkzor9.png)

## 2. License

```
MIT License

Copyright (c) 2022 Ye Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. Run Examples

### 3.1 set PATH in config.py as '../example/270909067.txt'

### 3.2 cd scripts

### 3.3 python ./show_gui.py

## 4. Video

https://user-images.githubusercontent.com/18455758/217151746-c024a281-d0dc-45e8-a4c4-8cd3b6cc8776.mp4



