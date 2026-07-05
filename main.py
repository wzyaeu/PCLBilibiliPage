from bilibili_api import sync, rank, hot

import os
import shutil
import json
import time
import secrets

def load_template(name):
    print(f'load_template-加载模板文件-{name}')
    global templates
    if not name in templates:
        t_path = os.path.join(BASE_PATH, 'templates', name+'.xaml')
        with open(t_path,'r', encoding='utf-8') as f:
            templates[name] =  f.read()

def save_output_file(name, data):
    print(f'save_output_file-保存输出文件-{name}')
    o_path = os.path.join(BASE_PATH, 'output', name)
    with open(o_path,'w', encoding='utf-8') as f:
        f.write(data)

def replaces(string: str, s: dict):
    output = string
    for l, d in s.items():
        output = output.replace('{'+l+'}', str(d))
    return output

def uninumber(n: int):
    if n >= 100000000:
        return '{:.1f}'.format(n/100000000) + '亿'
    elif n >= 10000:
        return '{:.1f}'.format(n/10000) + '万'
    else:
        return n

def escape_xaml(text):
    return (
        text.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;")
    )

def mainpage():
    print('mainpage-开始')
    print('mainpage-加载模板')
    load_template('mainpage')
    load_template('video')
    print('mainpage-获取api数据')
    video_data: dict = sync(hot.get_hot_videos(ps=12)) # type: ignore
    print('mainpage-构建页面')
    output = replaces(templates['mainpage'],{
        'video':'\n'.join([
            replaces(templates['video'],{
                'img': v['pic'],
                'view': uninumber(v['stat']['view']),
                'danmaku': uninumber(v['stat']['danmaku']),
                'date': time.strftime('%m/%d', time.localtime(v['pubdate'])),
                'up': escape_xaml(v['owner']['name']),
                'title': escape_xaml(v['title']),
                'url': escape_xaml(v['short_link_v2']),
                'desc': escape_xaml(v['desc']),
                'like': uninumber(v['stat']['like']),
                'coin': uninumber(v['stat']['coin']),
                'favorite': uninumber(v['stat']['favorite']),
                'share': uninumber(v['stat']['share']),
                '':print(f'mainpage-video-构建内容-{index}/{len(video_data['list'])}')
            }) for index, v in enumerate(video_data['list'],start=1)
        ]),
        'gv':BUILD_VERSION
    })
    print('mainpage-保存输出文件')
    save_output_file('Custom.xaml',output)
    save_output_file('Custom.xaml.ini',BUILD_VERSION)

def rankpage():
    print('rankpage-开始')
    print('rankpage-加载模板')
    load_template('rankpage')
    load_template('rankpage-next')
    load_template('video-rank')
    print('rankpage-获取api数据')
    video_data: dict = sync(rank.get_rank()) # type: ignore
    video_list = video_data['list']
    chunk_size = 20
    video_lists = [video_list[i:i + chunk_size] for i in range(0, len(video_list), chunk_size)]
    all_output = []
    print('rankpage-构建页面')
    for vlindex, vl in enumerate(video_lists, start=1):
        print(f'rankpage-构建页面-{vlindex}/{len(video_lists)}')
        output = replaces(templates['rankpage'],{
            'num':vlindex,
            'total':len(video_lists),
            'video':'\n'.join([
                replaces(templates['video-rank'],{
                    'img': v['pic'],
                    'view': uninumber(v['stat']['view']),
                    'danmaku': uninumber(v['stat']['danmaku']),
                    'date': time.strftime('%m/%d', time.localtime(v['pubdate'])),
                    'up': escape_xaml(v['owner']['name']),
                    'title': escape_xaml(v['title']),
                    'url': escape_xaml(v['short_link_v2']),
                    'desc': escape_xaml(v['desc']),
                    'like': uninumber(v['stat']['like']),
                    'coin': uninumber(v['stat']['coin']),
                    'favorite': uninumber(v['stat']['favorite']),
                    'share': uninumber(v['stat']['share']),
                    'color': '#ffbe35' if index == 1 else
                    '#99bce0' if index == 2 else
                    '#f5b7a3' if index == 2 else
                    '#7b859a',
                    'rank': index,
                    '':print(f'rankpage-video-构建内容-{vlindex}/{len(video_lists)}-{index}/{len(video_data['list'])}')
                }) for index, v in enumerate(vl,start=1+(vlindex-1)*20)
            ]),
            'next': '' if vlindex == len(video_lists) else replaces(templates['rankpage-next'],{
                'num':vlindex+1
            }),
        })

        all_output.append(output)
    print('rankpage-保存输出文件')
    for index, o in enumerate(all_output, start=1):
        print(f'rankpage-保存输出文件-{index}/{len(video_lists)}')
        save_output_file(f'rank_{index}.json',json.dumps(
            {
                "Title": f"Bilibili 全站排行榜 | 第 {index} / {len(video_lists)} 页"
            }
        ,ensure_ascii=False))
        save_output_file(f'rank_{index}.xaml',o)
    
def init():
    print('init-初始化中')
    global OUTPUT_PATH, BASE_PATH, BUILD_VERSION, templates
    templates = {}
    BUILD_VERSION = secrets.token_hex(4)
    BASE_PATH = os.path.dirname(__file__)
    OUTPUT_PATH = os.path.join(BASE_PATH,'output')
    shutil.rmtree(OUTPUT_PATH,ignore_errors=True)
    os.makedirs(OUTPUT_PATH,exist_ok=True)

    print('init-运行mainpage')
    mainpage()
    print('init-运行rank')
    rankpage()

init()