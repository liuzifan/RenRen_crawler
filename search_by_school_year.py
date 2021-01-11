import requests
import re
import random
import datetime

# 实现功能：
#     通过学校和入学年份，遍历爬取人人网中的用户ID，并将ID输出为一个文件


# 函数功能：
#     获取所需要的学校ID列表，入学年列表，已有ID全集
def get_all():
    # 提取学校列表，存于school_list
    school_list = []
    file_school = open("./id/school_id.txt", 'r', encoding="utf-8")
    line = file_school.readline()
    while line:
        line = line.strip()
        school_list.append(line)
        line = file_school.readline()
    file_school.close()

    # 提取年份列表
    year_list = []
    for i in range(1980, 2017):
        year_list.append(str(i))
    
    # 读已有的列表全集
    all_dict = {}
    all_list = []
    file_all = open("./id/all", 'r', encoding="utf-8")
    line = file_all.readline()
    while line:
        line = line.strip()
        all_dict[line] = "1"
        all_list.append(line)
        line = file_all.readline()
    file_all.close()
    print(f"len(all_dict)={len(all_dict)}")
    print(f"len(all_list)={len(all_list)}")
    
    return school_list, year_list, all_list, all_dict


if __name__ == '__main__':
    # 输入代理和请求头
    proxy = {}
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    
    # 获取年月日方便命名
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    
    # 获取学校列表，年份列表和总ID列表
    school_list, year_list, all_list, all_dict = get_all()

    # 使用session发送post请求，cookie保存在其中，在使用session进行请求登陆之后才能访问的地址
    session = requests.session()
    post_url = "http://www.renren.com/PLogin.do"
    post_data = {"email": "自己创建账号", "password": "密码"}
    session.post(post_url, data=post_data, proxies=proxy, headers=headers)
    # 这是按条件搜索页面url
    for n in range(len(school_list)):
        for m in range(len(year_list)):
            # 通过随机一个user模仿登录，防止反爬虫
            random_num = random.randrange(0, len(all_list))
            rand_user = all_list[random_num]
            print(f"rand_user={rand_user}")
            print(school_list[n])
            print(year_list[m])
            # 其中count代表翻页
            count = 0
            while 1:
                url = 'http://browse.renren.com/sAjax.do?ref_search=&q=&p=%5B%7B%22t%22%3A%22univ%22%2C%22' \
                'name%22%3A%22{0}%22%2C%22id%22%3A%22{2}%22%2C%22year%22%3A%22{1}%22%7D%5D&s=0&u={3}&act=search' \
                '&offset={4}&sort=0'.format('清华大学', year_list[m], school_list[n], rand_user, count)
                try:
                    r = session.get(url, timeout=2, proxies=proxy, headers=headers)
                except Exception as e:
                    print(e)
                    continue
                today = str(year) + str(month) + str(day)
                file_path = './id/lst' + today
                with open(file_path, "a+") as f:
                    f_all = open("./id/all", "a+")
                    x = re.findall('<strong>.*id=(\d+)', str(r.text))
                    for i in range(len(x)):
                        #去重操作
                        if all_dict.__contains__(x[i]):
                            print(f"exists:" + x[i])
                        else:
                            f.write(x[i]+'\n')
                            f_all.write(x[i]+'\n')
                            all_dict[x[i]] = "1"
                            print(f"add:" + x[i])
                    f_all.close()
                f.close()
                print(count)
                count += 10
                if count % 500 == 0:
                    count = 0
                    break
            print(m)
        print(n)
