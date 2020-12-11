import json


class wash():
    def __init__(self):
        self.FILE_NAME = './json/lessons_info.json'
        self.start()

    def start(self):
        self.load()
        self.see()
        self.save()

    def load(self):
        with open(self.FILE_NAME, 'r') as f:
            text = f.read()
        self.json_data = json.loads(text)

    def save(self):
        with open(self.FILE_NAME, 'w+') as f:
            f.write(json.dumps(self.json_data))

    def see(self):
        for key_1 in self.json_data.keys():
            word = self.json_data[key_1]['content']['tasks']['word']
            for key_2 in word:
                print("key_1:"+key_1+" key_2:" + key_2)
                print('题目：'+word[key_2]['name'])
                print('答案：'+word[key_2]['answer'])
                print('答案是否符合预期？回车符合其他不符合，清洗为：还没来得及写，勉强过一下吧。。。。。。。。。。。')
                code = input("")
                if code == '':
                    print('--->符合<---')
                    continue
                else:
                    self.json_data[key_1]['content']['tasks']['word'][key_2]['answer'] = '还没来得及写，勉强过一下吧。。。。。。。。。。。'
                    print('--->清洗为标准解释<---')


a = wash()
