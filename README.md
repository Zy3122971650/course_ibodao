---
tittle: ibodao刷课
---
ibodao对视频没有防作弊的机制，训练题的拖拽题可以直接请求到答案，上传题又很久没有人审核了，所以就......
## 目录结构

```
.
├── collect_major.py
├── json
│   └── lessons_info.json
├── main.py
├── README.md
└── wash_word_answer.py
```
## 文件解读
|文件|作用|
|---|---|
|`collect_major.py`|收集课程信息和答案|
|`wash_word_answer.py`|清洗上传题里面奇怪的答案|
|`main.py`|刷题的主程序|
  
## 使用方法
在`main.py`中的`main`函数里添加自己的帐号和密码，然后`python main.py`