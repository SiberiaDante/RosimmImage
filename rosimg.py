#!/usr/bin/env python
# coding=utf-8
import os
import time
import threading
from multiprocessing import Pool, cpu_count
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.rosimm8.com"
}
"""
图片存储路径
"""
DIR_PATH = r"E:\rosimg"

"""
将图片下载到本地文件夹
"""
def save_pic(pic_url, ros_cnt):
    try:
        img = requests.get(pic_url, headers=HEADERS, timeout=10)
        img_name = "ros_cnt{}.jpg".format(ros_cnt)
        with open(img_name, 'ab') as f:
            f.write(img.content)
            print(img_name)
    except Exception as e:
        print(e)

"""
新建套图文件夹并切换到该目录下
"""
def make_dir(folder_name):
    path = os.path.join(DIR_PATH, folder_name)
    # 如果目录已经存在就不用再次爬取了，去重，提高效率。存在返回 False，否则反之
    if not os.path.exists(path):
        os.makedirs(path)
        print('---path---'+path)
        os.chdir(path)
        return True
    print("Folder has existed!")
    return False


def delete_empty_dir(save_dir):
    """
    如果程序半路中断的话，可能存在已经新建好文件夹但是仍没有下载的图片的
    情况但此时文件夹已经存在所以会忽略该套图的下载，此时要删除空文件夹
    """
    if os.path.exists(save_dir):
        if os.path.isdir(save_dir):
            for d in os.listdir(save_dir):
                path = os.path.join(save_dir, d)     # 组装下一级地址
                if os.path.isdir(path):
                    delete_empty_dir(path)      # 递归删除空文件夹
        if not os.listdir(save_dir):
            os.rmdir(save_dir)
            print("remove the empty dir: {}".format(save_dir))
    else:
        print("Please start your performance!")


lock = threading.Lock()     # 全局资源锁


def main_start(url):
    """
    爬虫入口，主要爬取操作
    """
    try:
        r = requests.get(url+'.html', headers=HEADERS, timeout=10).text
        print(url+'.html')
        name_index = 0
        # 套图名，也作为文件夹名
        folder_name = BeautifulSoup(r, 'lxml').find(
            'h1',class_='article-title').find('a').text.encode('ISO-8859-1').decode('utf-8')
        with lock:
            if make_dir(folder_name):
                # 套图张数
                max_count = BeautifulSoup(r, 'lxml').find(
                    'div',class_='pagination2').find_all('li')[-2].find('a').get_text()
                print('-------max_count-----'+max_count)
                # 套图页面
                page_urls=[]
                for i in range(1,(int(max_count)+1)):
                    if i==1:
                        page_urls.append(url + '.html')
                    else:
                        page_urls.append(url + '_' + str(i)+'.html')

                # 图片地址
                for index, page_url in enumerate(page_urls):
                    print('-----page_url-----'+page_url)
                    result = requests.get(
                        page_url, headers=HEADERS, timeout=10).text
                    img_url=BeautifulSoup(result,'lxml').find('article',class_='article-content').find_all('img')
                    for s_img_url in img_url:
                        real_img='http://www.rosimm8.com'+s_img_url.get('src')
                        print('-----real_img-----'+real_img)
                        name_index=name_index+1
                        save_pic(real_img,name_index)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    urls = ['http://www.rosimm8.com/rosimm/{cnt}'.format(cnt=cnt) for cnt in range(416, 2528)]
    pool = Pool(processes=cpu_count())
    try:
        delete_empty_dir(DIR_PATH)
        pool.map(main_start, urls)
    except Exception:
        time.sleep(30)
        delete_empty_dir(DIR_PATH)
        pool.map(main_start, urls)