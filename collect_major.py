import requests
from bs4 import BeautifulSoup
import json
import time

lessons_info = {}
FILE_NAME = './json/lessons_info.json'
USERNAME = 'xxx'
PASSWD = 'xxx'


def main():
    s = requests.session()
    s = login(s)
    get_save_train_id(s)
    get_save_info(s)
    save_to_json()


def init_json() -> dict:
    print("加载原有数据")
    import os
    if not os.path.exists(FILE_NAME):
        print('不存在原有数据')
        return {}
    with open(FILE_NAME, 'r') as f:
        st = f.read()
    return json.loads(st)


def save_course_html(response, courses_html):
    html = json.loads(response.text)['data']
    courses_html.append(html)


def save_to_json():
    print('---写入json文件---')
    with open(FILE_NAME, 'w+') as f:
        f.write(json.dumps(lessons_info))
    print('---写入完成----\n---脚本关闭----')


def login(s):
        url = 'http://www.ibodao.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        }

        s.get(url, headers=headers)
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
            'loginname': USERNAME,
            'loginpw': PASSWD,
            'autologin': '1'
        }

        s.post('http://www.ibodao.com/Member/login.html',
                                 headers=headers, data=data, verify=False)


        return s


def get_save_info(s):
    alredy_info = init_json()
    for train_id in lessons_info.keys():
        lessons_info[train_id]['all'] = '0'
        if train_id in alredy_info.keys() and alredy_info[train_id]['all'] == '1':
            print('代码为：{}的课程已在数据库中，且收集完毕......'.format(train_id))
            lessons_info[train_id]['all'] = '1'  # 防止字典不按预期和并
            continue
        # time.sleep(0.5)
        print('---解析{}---'.format(train_id))
        get_save_base_info(train_id, s)
        get_save_content(train_id, s)
        lessons_info[train_id]['all'] = '1'
    print('-----全部信息解析完毕-----\n合并已有数据')
    lessons_info.update(alredy_info)
    pass


def get_save_content(train_id, s):
    lesson = lessons_info[train_id]
    lesson['content'] = {}
    content = lesson['content']
    # 视频部分
    print('------解析视频信息-------')
    get_save_video_content(content, train_id, s)

    # 实训部分
    print('-----解析实训信息------')
    get_save_tasks_content(content, train_id, s)

    # 测验部分
    print('-------解析测验信息------')
    get_save_exam_content(content, train_id, s)


def get_save_exam_content(content, train_id, s):
    content['exam'] = {}
    exam = content['exam']
    url = 'http://www.ibodao.com/User/Train/train/type/survey/id/{}.html'.format(
        train_id)
    response = s.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    first_div = soup.find_all('div', class_='row testInfo on')
    for div in first_div:
        exam_id = div['data-id']
        name = div.find(
            'div', class_='col-md-9 testTitle text_over_hid')['title']
        answer = ''
        print('测验信息：测验代号：{}，测验名称：{}，测验答案：{}'.format(exam_id, name, answer))
        exam[exam_id] = {
            'answer': answer,
            'name': name
        }


def get_save_tasks_content(content, train_id, s):
    # 实训部分
    content['tasks'] = {}
    tasks = content['tasks']
    tasks['drag'] = {}
    drag = tasks['drag']
    tasks['word'] = {}
    word = tasks['word']
    url = 'http://www.ibodao.com/User/Train/train/type/task/id/{}.html'.format(
        train_id)
    response = s.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    first_div = soup.find_all('div', class_='row testInfo on')
    for div in first_div:
        task_id = div['data-id']
        qus_type = div.find('i')['title']
        name = div.find(
            'div', class_='col-md-9 col-xs-12 shixun-Title text_over_hid')['title']
        if '拖' in qus_type:
            answer = get_save_drag_answer(s, task_id)
            drag[task_id] = {
                'answer': answer,
                'name': name
            }
        elif '上' in qus_type:
            answer = get_save_word_answer(s,task_id)
            word[task_id] = {
                'answer': answer,
                'name': name
            }
        print('任务信息：任务代号：{}，任务类型：{}，任务名称：{}，测验答案：{}'.format(
            task_id, qus_type, name, answer))


def get_save_word_answer(s, task_id) -> str:
    headers = {
        'X-Requested-With': 'XMLHttpRequest',

        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    url = 'http://www.ibodao.com/User/task/discuss/task_id/{}.html'.format(
        task_id)
    json_data = s.get(url, headers=headers).text
    soup = BeautifulSoup(json.loads(json_data)['data'], 'lxml')
    all_answer = soup.find_all('div', class_='clearfix commentRight')
    length_1 = 0
    answer = ' '
    for a in all_answer:
        text = a.find('p').get_text()
        length = len(text)
        if length > length_1:
            answer = text
            length_1 = length
    return answer


def get_save_drag_answer(s, task_id) -> str:

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'task_id': task_id
    }
    response = s.post('http://www.ibodao.com/User/task/watch_answer.html',
                      headers=headers, data=data, verify=False)
    result = json.loads(response.text)['data']

    new_answer = []
    for key in result.keys():
        temp = {}
        temp['k'] = key
        temp['v'] = result[key]
        new_answer.append(temp)
    return json.dumps(new_answer)


def get_save_video_content(content, train_id, s):
    # 视频部分
    content['videos'] = {}
    videos = content['videos']
    url = 'http://www.ibodao.com/User/Train/train/type/video/id/{}.html'.format(
        train_id)
    response = s.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    first_divs = soup.find_all('div', class_='row testInfo on')
    for div in first_divs:
        video_id = div['data-id']
        name = div.find('div', class_='video-title')['title']
        total_time = div.find(
            'div', class_='video-time').get_text().strip('", ,\n')
        total_time = str(int(total_time.split(
            ':')[-2])*60 + int(total_time.split(':')[-1]))  # 需要改进，考虑使用递归加入对小时的计算
        print("视频信息：视频ID：{} 视频名字：{} 视频全长：{}s".format(video_id, name, total_time))
        # 写入字典
        videos[video_id] = {
            'name': name,
            'total_time': total_time
        }


def get_save_base_info(train_id, s):
    lesson = lessons_info[train_id]
    # 构造URL
    url = 'http://www.ibodao.com/User/Train/train/id/{}.html'.format(train_id)
    response = s.get(url)
    # 解析html
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    fist_div = soup.find('div', class_='subInfo clearfix')
    left_div = fist_div.find('div', class_='pull-left shixun-title-left')
    right_div = fist_div.find('div', class_='shixun-title-down')

    name = left_div.find('h2').get_text()

    info_raws = left_div.find_all('p')
    for info_raw in info_raws:
        infos = info_raw.get_text()
        if '方向' in infos:
            direction = infos.split('：')[-1].strip(' ')
        elif '难度' in infos:
            diffculty = infos.split('：')[-1].strip(' ')

    info_raws = right_div.find_all('li')
    for info_raw in info_raws:
        num = info_raw.find('p').get_text()
        if '课程' in info_raw.get_text():
            videos = num
        elif '训练' in info_raw.get_text():
            tasks = num
        elif '测验' in info_raw.get_text():
            exam = num

    # 写入字典
    print("课程名字：{} \n难度：{} 课程方向：{} 视频个数：{} 实训个数：{} 测验个数：{}\n".format(
        name, diffculty, direction, videos, tasks, exam))
    lesson['base_info'] = {
        'name': name,
        'direction': direction,
        'diffculty': diffculty,
        'videos': videos,
        'tasks': tasks,
        'exam': exam
    }


def get_save_train_id(s):
    train_ids = []
    # 获取第一页数据
    url = 'http://www.ibodao.com/User/Train/index.html'
    params = {}
    params['_'] = int(time.time())
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = s.get(url, params=params, headers=headers)
    if response.status_code != requests.codes['ok']:
        print('获取课程信息初始化失败\n脚本退出')
        exit(1)
    print('成功课程初始化完成\n已收集第一页课程数据')

    # 分析第一页数据
    parse_train_id(response, train_ids)

    ######获取页数######
    print('获取课程页面数量:', end='')
    num = get_pages_num(response)
    print('共{}页还需要收集{}页'.format(num, num-1))
    ####################

    print('----------开始收集数据---------')
    for i in range(2, num+1):
        params['level'] = '-1'
        params['order'] = '1'
        params['p'] = i
        params['_'] = int(time.time())
        response = s.get(url, params=params, headers=headers)
        parse_train_id(response, train_ids)
        print(i)
    print("-----收集完毕------")

    # 写入字典
    for train_id in train_ids:
        lessons_info[train_id] = {}


def get_pages_num(response):
    html = json.loads(response.text)['data']
    soup = BeautifulSoup(html, 'lxml')
    nums = soup.find_all('a', class_='num')
    num = nums[-1].get_text()
    num = int(num)
    return num


def parse_train_id(response, train_ids):
    html = json.loads(response.text)['data']
    soup = BeautifulSoup(html, 'lxml')
    first_step_find_divs = soup.find_all('div', class_='pt-item-board')
    for div in first_step_find_divs:
        info = div.find('a')
        train_ids.append(info['href'].split('/')[-1][:-5])


main()
