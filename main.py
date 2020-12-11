import requests
import time
import json
import random
from threading import Thread
from bs4 import BeautifulSoup


class my_thread(Thread):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        pass

    def mprint(self, string, end='\n'):
        print('当前用户：'+self.user_info['username'] + '===>' + string, end=end)

    def run(self):
        self.s = requests.session()
        self.login()
        lessons = self.load_major_info()
        self.donging(lessons)

    def login(self):
        url = 'http://www.ibodao.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        }

        self.s.get(url, headers=headers)
        headers = {
            'Proxy-Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.ibodao.com',
            'Referer': 'http://www.ibodao.com/Member/login.html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        data = {
            'loginname': self.user_info['username'],
            'loginpw': self.user_info['passwd'],
            'autologin': '1'
        }

        self.s.post('http://www.ibodao.com/Member/login.html',
                                 headers=headers, data=data, verify=False)

        self.mprint('cookie初始化成功')

    def load_major_info(self):
        self.mprint("加载数据")
        import os
        if not os.path.exists('./json/lessons_info.json'):
            return {}
        with open('./json/lessons_info.json', 'r') as f:
            st = f.read()
        return json.loads(st)

    def donging(self, lessons):
        for lesson in lessons.keys():
            name = lessons[lesson]['base_info']['name']
            direction = lessons[lesson]['base_info']['direction']
            diffculty = lessons[lesson]['base_info']['diffculty']
            videos = lessons[lesson]['base_info']['videos']
            tasks = lessons[lesson]['base_info']['tasks']
            if direction not in ["互联网", "电子商务基础", "网络营销基础", "SEO/SEM", "微博营销", "微信营销",'新媒体营销','软文/内容营销','邮件/IM/知识营销','其他']:
                self.mprint(direction+" 不在需要完成的内容里")
                continue
            self.mprint('---正在进行{} 难度{} 方向：{} 视频：{} 实训：{}---'.format(name,
                                                                     diffculty, direction, videos, tasks))
            self.do_video(lessons[lesson]['content']['videos'], lesson)
            self.do_drag(lessons[lesson]['content']['tasks']['drag'], lesson)
            self.do_doc(lessons[lesson]['content']['tasks']['word'], lesson)

    def do_video(self, videos, train_id):
        for video in videos.keys():
            name = videos[video]['name']
            self.mprint('Video:{}'.format(name))
            totol_time = videos[video]['total_time']

            data = {
                'id': video,
                'cid': ''
            }
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }

            self.s.post('http://www.ibodao.com/video/playvideo.html',
                        headers=headers, data=data, verify=False)

            url = 'http://www.ibodao.com/video/research_time.html?id={}&cid=&research_time={}&claid=0'.format(
                video, totol_time)
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }

            self.mprint('URL：{}，\nResponse------>'.format(url), end='')
            response = self.s.get(url, headers=headers)
            if response.text == '1':
                self.mprint('ok')
            else:
                url = 'http://www.ibodao.com/Video/info/id/{}/tid/{}.html'.format(
                    video, train_id)
                headers = {
                    'Upgrade-Insecure-Requests': '1',
                }
                response = self.s.get(url, headers=headers)
                txt_lst = response.text.split('\n')
                txt_lst.reverse()
                for t in txt_lst:
                    if 'my_study_time = parseInt' in t:
                        code = ('def parseInt(a):return a\n')
                        exec(code+t.strip('\n \r , '))
                        if locals()['my_study_time'] == totol_time:
                            self.mprint('ok')
                        else:
                            self.mprint('error')
            self.mprint('sleep 2s')
            time.sleep(1)

    def do_drag(self, tasks, train_id):
        for task in tasks:
            name = tasks[task]['name']
            self.mprint('Drag:{}'.format(name))
            answer = tasks[task]['answer']

            url = 'http://www.ibodao.com/User/Task/start/task_id/{}/train_id/{}.html'.format(
                task, train_id)
            headers = {
                'Upgrade-Insecure-Requests': '1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            }
            self.mprint('Start: Get request')
            response = self.s.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            text = soup.find('i', class_='icon icon-jinxingzhong').get_text()
            if '重新挑战' == text:
                self.mprint('已经挑战过了')
                continue

            self.mprint('Sleep: Wait 2s')
            time.sleep(2)

            headers = {
                'X-Requested-With': 'XMLHttpRequest',
            }
            data = {
                'task_id': task,
                'user_answer': answer,
                'train_id': train_id
            }
            url = 'http://www.ibodao.com/User/Task/start.html'
            self.mprint('info: Post answer')
            response = self.s.post(url, headers=headers,
                                   data=data, verify=False)
            result = json.loads(response.text)
            result = result['data']
            level = result['score_level']
            correct_rate = result['correct_rate']
            total_time = result['total_time']
            result = "评估等级：{}，正确率：{}%，用时{}".format(
                level, correct_rate, total_time)
            self.mprint('Result'+result)

    def do_doc(self, tasks, train_id):
        for task in tasks:
            name = tasks[task]['name']
            self.mprint('Task:{}'.format(name))
            url = 'http://www.ibodao.com/User/Task/start/task_id/{}/train_id/{}.html'.format(
                task, train_id)
            headers = {
                'Upgrade-Insecure-Requests': '1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            }
            self.mprint('Start: Get request')
            response = self.s.get(url, headers=headers)
            if '重新挑战' in response.text:
                self.mprint('已经挑战过了')
                continue

            ###
            # 构造answer
            answer = tasks[task]['answer']
            ###
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
            }
            data = {
                'task_id': task,
                'info': answer,
                'isdone': '',
                'train_id': train_id
            }
            url = 'http://www.ibodao.com/User/Task/start.html'
            self.mprint('info: Post answer')
            self.s.post(url, headers=headers,
                        data=data, verify=False)



def main():
    user_infos = [
        {'username': 'xxx', 'passwd': 'xxx'},
    ]
    tasks = []
    for user_info in user_infos:
        tasks.append(my_thread(user_info))
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()

    print('All Done')


main()
