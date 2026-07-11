from bilibili_api import sync, rank, hot

import os
import shutil
import json
import time
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from enum import Enum

class RankType_NameEx(Enum):
    All = {"api_type": "x", "rid": 0, "type": "all", "name": "全部"}
    Bangumi = {"api_type": "pgc", "season_type": 1, "name": "番剧"}
    GuochuangAnime = {"api_type": "pgc", "season_type": 4, "name": "国产动画"}
    Guochuang = {"api_type": "x", "rid": 168, "type": "all", "name": "国创相关"}
    Documentary = {"api_type": "pgc", "season_type": 3, "name": "纪录片"}
    Douga = {"api_type": "x", "rid": 1005, "type": "all", "name": "动画"}
    Music = {"api_type": "x", "rid": 1003, "type": "all", "name": "音乐"}
    Dance = {"api_type": "x", "rid": 1004, "type": "all", "name": "舞蹈"}
    Game = {"api_type": "x", "rid": 1008, "type": "all", "name": "游戏"}
    Knowledge = {"api_type": "x", "rid": 1010, "type": "all", "name": "知识"}
    Technology = {"api_type": "x", "rid": 1012, "type": "all", "name": "科技数码"}
    Sports = {"api_type": "x", "rid": 1018, "type": "all", "name": "运动"}
    Car = {"api_type": "x", "rid": 1013, "type": "all", "name": "汽车"}
    Life = {"api_type": "x", "rid": 160, "type": "all", "name": "生活"}
    Food = {"api_type": "x", "rid": 1020, "type": "all", "name": "美食"}
    Animal = {"api_type": "x", "rid": 1024, "type": "all", "name": "动物圈"}
    Kichiku = {"api_type": "x", "rid": 1007, "type": "all", "name": "鬼畜"}
    Fashion = {"api_type": "x", "rid": 1014, "type": "all", "name": "时尚美妆"}
    Ent = {"api_type": "x", "rid": 1002, "type": "all", "name": "娱乐"}
    Cinephile = {"api_type": "x", "rid": 1001, "type": "all", "name": "影视"}
    Movie = {"api_type": "pgc", "season_type": 2, "name": "电影"}
    TV = {"api_type": "pgc", "season_type": 5, "name": "电视剧"}
    Variety = {"api_type": "pgc", "season_type": 7, "name": "综艺"}
    Original = {"api_type": "x", "rid": 0, "type": "origin", "name": "原创"}
    Rookie = {"api_type": "x", "rid": 0, "type": "rookie", "name": "新人"}

def load_template(name, noxaml = False):
    print(f'load_template-加载模板文件-{name}')
    global templates
    if not name in templates:
        t_path = os.path.join(BASE_PATH, 'templates', name+('' if noxaml else '.xaml'))
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
                'tag': '',
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

def rankpage(type_: RankType_NameEx | None = None):
    print('rankpage-开始')
    print('rankpage-加载模板')
    load_template('video')
    load_template('rankpage')
    load_template('rankpage-next')
    load_template('rankpage-videotag')
    if type_ == None:
        print('rankpage-总榜模式')
        print('rankpage-获取api数据')
        video_data: dict = sync(rank.get_rank()) # type: ignore
    else:
        print('rankpage-分榜模式')
        print(f'rankpage-分榜type {type_}')
        print('rankpage-获取api数据')
        video_data: dict = sync(rank.get_rank(type_)) # type: ignore
    video_list = video_data['list']
    chunk_size = 20
    video_lists = [video_list[i:i + chunk_size] for i in range(0, len(video_list), chunk_size)] if len(video_list) > 0 else [[]]
    all_output = []
    print(f'rankpage-构建页面')
    for vlindex, vl in enumerate(video_lists, start=1):
        print(f'rankpage-构建页面-{vlindex}/{len(video_lists)}')
        output = replaces(templates['rankpage'],{
            'num':vlindex,
            'listname':'全站排行榜' if type_ == None else f'{type_.value['name']}排行榜',
            'total':len(video_lists),
            'video':'\n'.join([
                replaces(templates['video'],{
                    'img': v['pic'] if 'pic' in v else v['ss_horizontal_cover'],
                    'view': uninumber(v['stat']['view']),
                    'danmaku': uninumber(v['stat']['danmaku']),
                    'date': time.strftime('%m/%d', time.localtime(v['pubdate'])) if 'pubdate' in v else '',
                    'up': escape_xaml(v['owner']['name']) if 'owner' in v else '',
                    'title': escape_xaml(v['title']),
                    'url': escape_xaml(v['short_link_v2'] if 'short_link_v2' in v else v['url']),
                    'desc': escape_xaml(v['desc']) if 'desc' in v else '-',
                    'like': uninumber(v['stat']['like'] if 'like' in v['stat'] else v['stat']['follow']),
                    'coin': uninumber(v['stat']['coin']) if 'coin' in v['stat'] else '',
                    'favorite': uninumber(v['stat']['favorite']) if 'favorite' in v['stat'] else '',
                    'share': uninumber(v['stat']['share']) if 'share' in v['stat'] else '',
                    'tag':replaces(templates['rankpage-videotag'],{
                        'color': '#ffbe35' if index == 1 else(
                        '#99bce0' if index == 2 else(
                        '#f5b7a3' if index == 3 else
                        '#7b859a')),
                        'rank': index,
                    }),
                }) for index, v in enumerate(vl,start=1+(vlindex-1)*20)
            ]),
            'next': '' if vlindex == len(video_lists) else replaces(templates['rankpage-next'],{
                'num':vlindex+1,
                'ltype':'overall' if type_ == None else type_._name_
            }),
        })

        all_output.append(output)
    print('rankpage-保存输出文件')
    for index, o in enumerate(all_output, start=1):
        print(f'rankpage-保存输出文件-{index}/{len(video_lists)}')
        if type_ == None:
            save_output_file(f'overall_rank_{index}.json',json.dumps(
                {
                    "Title": f"Bilibili 全站排行榜 | 第 {index} / {len(video_lists)} 页"
                }
            ,ensure_ascii=False))
            save_output_file(f'overall_rank_{index}.xaml',o)
        else:
            save_output_file(f'{type_._name_}_rank_{index}.json',json.dumps(
                {
                    "Title": f"Bilibili {type_.value["name"]}排行榜 | 第 {index} / {len(video_lists)} 页"
                }
            ,ensure_ascii=False))
            save_output_file(f'{type_._name_}_rank_{index}.xaml',o)

def ranklistpage(rank_l):
    print('ranklistpage-开始')
    print('ranklistpage-加载模板')
    load_template('ranklistpage')
    load_template('ranklistpage-item')
    output = ''
    for index, listtype in enumerate(rank_l, start=1):
        if listtype._name_ in ['All']:
            continue
        print(f'ranklistpage-添加排行榜-{listtype._name_}')
        output += replaces(templates['ranklistpage-item'],{
            'name':listtype.value['name'],
            'mrank':listtype._name_,
            'num':index-1
        })
    output = replaces(templates['ranklistpage'],{
        'item':output,
    })
    print('ranklistpage-保存输出文件')
    save_output_file(f'rank_list.json',json.dumps(
        {
            "Title": f"排行榜分类"
        }
    ,ensure_ascii=False))
    save_output_file(f'rank_list.xaml',output)

def weekpage():
    print('weekpage-开始')

    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    
    print('weekpage-加载模板')
    load_template('weekpage')
    load_template('video')

    delta_days = (now - datetime(2019, 3, 22, tzinfo=ZoneInfo("Asia/Shanghai"))).days
    week_number = delta_days // 7

    print(f'weekpage-获取api数据-第{week_number}周')
    video_data: dict = sync(hot.get_weekly_hot_videos(week=week_number)) # type: ignore

    print('weekpage-构建页面')
    output = replaces(templates['weekpage'],{
        'num':week_number,
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
                '':print(f'weekpage-video-构建内容-{index}/{len(video_data['list'])}')
            }) for index, v in enumerate(video_data['list'],start=1)
        ])
    })
    print('weekpage-保存输出文件')
    save_output_file(f'week.json',json.dumps(
        {
            "Title": f"Bilibili 每周必看 | 第 {week_number} 期"
        }
    ,ensure_ascii=False))
    save_output_file(f'week.xaml',output)

def sfile():
    print('sfile-保存build_info.md')
    load_template('build_info.md',noxaml=True)
    save_output_file(f'build_info.md',replaces(templates['build_info.md'],{
        'build_version':BUILD_VERSION
    }))

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
    rank_l = list(RankType_NameEx._member_map_.values())
    rankpage()
    for listtype in rank_l:
        if listtype._name_ in ['All']:
            continue
        print(f'init-运行rank-{listtype._name_}分榜')
        rankpage(listtype) # type: ignore

    print('init-运行ranklist')
    ranklistpage(rank_l)

    # print('init-运行weekpage')
    # weekpage()


    print('init-运行sfile')
    sfile()

init()