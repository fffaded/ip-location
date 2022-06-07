import re
import requests
import json
import time
import random

'''
    获取IP对应的C类地址
'''
def get_C_network(ip):
    return re.sub("\d+$", "0", ip)


'''
    选出属于某一城市和ISP的所有IP网段
'''
def get_city_network(city, isp):
    match_num = 0
    match_ips = []
    # 直接选出网段
    pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})" + "[^\n]*" + city + "[^\n]*" + isp

    # 逐行搜索
    with open("cz.txt", "r", encoding="gb18030") as f:
        while True:
            line = f.readline()
            if line == "":
                break
            result = re.findall(pattern, line)
            if len(result) != 0:
                match_ips.append(result[0])
                match_num += 1
        print("搜索结束！一共搜索到%d个符合%s,%s条件的IP段。"%(match_num, city, isp))
    
    return match_ips

    
'''
    使用阿里云提供的IP归属地查询接口，检查IP网段与对应地理位置的映射关系是否正确
    核实后存储到$城市名.txt中
'''
def check_city_network(city, isp, ips):
    landmark_ips = []
    i = 0
    # API接口相关参数
    host = 'https://api01.aliyun.venuscn.com'
    path = '/ip'
    appcode = '47fdd737ef064f09ae8a8ed7d2a51943'
    headers = {"Authorization": 'APPCODE ' + appcode}
    f = open("./ip/"+str(city)+".txt","w+")
    # try except结构防止异常中止(主要是服务器挡住了IP)，实在不行就断断续续的抽取
    try:
        for ip in ips:
            ip_start = ip[0]
            ip_end = ip[1]
            url_1 = host + path + '?ip=' + ip_start 
            url_2 = host + path + '?ip=' + ip_end 
            response_1 = requests.get(url_1, headers=headers)
            response_2 = requests.get(url_2, headers=headers)
            if response_1.status_code == 200 and response_2.status_code == 200:
                if json.loads(response_1.text)["data"]["city"] == city and json.loads(response_1.text)["data"]["isp"] == isp and json.loads(response_2.text)["data"]["city"] == city and json.loads(response_2.text)["data"]["isp"] == isp:
                    landmark_ips.append(ip)
                    ip_start_C = get_C_network(ip_start)
                    ip_end_C = get_C_network(ip_end)
                    i += 1
                    f.write(ip_start +"," + ip_end +"," + ip_start_C +"," + ip_end_C + "\n")     
                    time.sleep(1)
                    print(i)
    except Exception as e:
        print(e)
        print("获取%s的IP地址时异常结束"%city)
        f.close()
    f.close()
    return landmark_ips

'''
    筛选出地标并将地标IP写入文件：每一个C类网络只有一个被用作地标IP
'''
def select_loc_ip(city):
    loc_ip = []
    last_network_end = "b"
    
    with open("./ip/"+city+".txt", "r") as f1:
        while True:
            line = f1.readline().strip("\n")
            if line == "":
                break
            ips = line.split(",")
            # 比较相邻两条记录之间的IP段范围来选择地标
            if last_network_end != ips[-2]:
                if ips[-1] == ips[-2]:
                    # IP段在同一个C类网络中，则使用一个IP
                    loc_ip.append(ips[0])
                else:
                    # IP段跨多个C类网络，则使用两个
                    loc_ip.append(ips[0])
                    loc_ip.append(ips[1])
            elif last_network_end != ips[-1]:
                loc_ip.append(ips[1])
            else:
                continue
            # 更新最新网段
            last_network_end = ips[-1]
    # 将选择出的地标写入文件
    f2 = open("./ip/"+city+"地标"+".txt", "w+")
    for ip in loc_ip:
        f2.write(ip+"\n")
    f2.close()

    return loc_ip


'''
    将地标IP分为训练集和测试集并写入文件
    训练集：120个
    测试集：30个
'''
def split_loc_ip(city):
    # 均选择选择30个测试,120个训练
    ips,ips_test,ips_train = [],[],[]
    with open("./ip/"+city+"地标.txt","r") as f:
        while True:
            line = f.readline().strip("\n")
            if line == "":
                break
            ips.append(line)
    random.shuffle(ips)
    ips_test = ips[:30]
    ips_train = ips[30:150]
    # 写入文件
    f1 = open("./ip/"+city+"训练.txt","w+")
    f2 = open("./ip/"+city+"测试.txt","w+")
    for item1 in ips_train:
        f1.write(item1+"\n")
    for item2 in ips_test:
        f2.write(item2+"\n")
    f1.close()
    f2.close()


# if __name__ == "__main__":
    # 长沙，广州，西安，郑州，杭州，武汉，成都
    # ips = get_city_network("长沙", "电信")
    # print("直接提取的IP网段有%d个"%len(ips))
    # ips = check_city_network("长沙", "电信", ips)
    # print("筛选后的IP网段有%d个"%len(ips))
    # ips = get_city_network("西安", "电信")
    # print("直接提取的IP网段有%d个"%len(ips))
    # ips = check_city_network("西安", "电信", ips)
    # print("筛选后的IP网段有%d个"%len(ips))
    # ips = get_city_network("南京", "电信")
    # print("直接提取的IP网段有%d个"%len(ips))
    # ips = check_city_network("南京", "电信", ips)
    # print("筛选后的IP网段有%d个"%len(ips))
    
    # 筛选出各个城市的地标IP
    # select_loc_ip("长沙")
    # select_loc_ip("西安")
    # # select_loc_ip("广州")
    # select_loc_ip("南京")
    # select_loc_ip("深圳")

    # 划分训练和测试IP，选择西安、长沙、广州
    # split_loc_ip("广州")
    # split_loc_ip("西安")
    # split_loc_ip("长沙")
    # split_loc_ip("南京")
    # split_loc_ip("深圳")