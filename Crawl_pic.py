import requests
import os
import re
import sys
import json


# 实现功能：
#     根据已爬取的ID列表，遍历ID来爬取每一个ID的照片，并根据ID名保存至相应文件夹。

# 代理和请求头
proxy = { }
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
}


# 函数功能：
#     通过session登录人人网
def log_in():
    session = requests.session()
    # 登录的表单url
    post_url = "http://www.renren.com/PLogin.do"
    post_data = {"email": "自己的账号", "password": "密码"}
    # 使用session发送post请求，cookie保存在其中
    # 在使用session进行请求登陆之后才能访问的地址
    session.post(post_url, data=post_data, proxies=proxy, headers=headers)
    return session


# 函数功能
#     获取一个ID的相片url的list之后，将图片下载到本地
def capture_pic(urllist, Idpath, Id):
    count = 0
    for url in urllist:
        picpath = Idpath+Id+'_'+str(count)+'.jpg'
        with open(picpath, "wb") as f:
            try:
                picture = requests.get(url, proxies=proxy, timeout=3, headers=headers)
                f.write(picture.content)
                print("%s下载成功" % picpath)
                count += 1
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    # savepath为图片保存路径，namelist为ID列表读取路径
    savepath = sys.argv[1]
    namelist = sys.argv[2]
    
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    session = log_in()
    f1 = open(namelist, 'r')
    lines = f1.readlines()
    # 遍历每一个ID
    for line in lines:
        urllist = []
        Id = line.strip('\n')
        # 访问ID的相册页面，找出该ID所有的相册，存入x中
        album_url = 'http://photo.renren.com/photo/{0}/albumlist/v7?offset=0&limit=40#'.format(Id)
        try:
            r = session.get(album_url, timeout=3, proxies=proxy, headers=headers)
            Idpath = savepath+Id+"/"
            if not os.path.exists(Idpath):
                os.makedirs(Idpath)
        except Exception as e:
            print(e)
            continue
        try:
            x = re.findall('"albumId":"(.*?)"', str(r.text))
        except Exception as e:
            print(e)
            continue
        num = 0
        # 针对每一个相册x，访问并提取相册内所有的照片，存入y中
        if len(x):
            for i in range(len(x)):
                pic_url = r'http://photo.renren.com/photo/{0}/album-{1}/v7'.format(Id,x[i])
                #print(pic_url)
                try:
                    r2 = session.get(pic_url, timeout=3, proxies=proxy, headers=headers)
                except Exception as e:
                    print(e)
                    continue
                try:
                    y = re.findall('"url":"(.*?)"', str(r2.text))
                except Exception as e:
                    print(e)
                    continue
                for j in range(len(y)):
                    Url = '/'.join(y[j].split('\/'))
                    urllist.append(Url)
                    num += 1
        # num为记录每个ID的照片数，如果照片数小于5，则不爬取该用户，如果大于200，则只爬取200张
        if num > 5:
            if num > 200:
                urllist = urllist[:200]
            capture_pic(urllist, Idpath, Id)
        else:
            os.rmdir(Idpath)
            print('delete noise {0}'.format(Id))
    print("all done")

