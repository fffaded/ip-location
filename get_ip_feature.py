import subprocess
import re


'''
    获取单个IP的中间路由器信息
    返回的结果包括了到某个区域所经过的中间路由器信息，即三元组<跳数，路由器IP，次数>
'''
def get_path_feature(ip):
    response = subprocess.Popen('traceroute -I -n -q 3 {}'.format(ip), 
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE).communicate()[0].decode("GBK")
    # 需要忽略前五跳和最后一跳
    pattern_1 = r"\n ?([6-9]|\d{2})[^\d]*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
    pattern_2 = r"\n ?\d+[^\d]*" + str(ip)
    res_1 = re.findall(pattern_1, response)
    res_2  = True if re.findall(pattern_2, response)!=[] else False
    temp = []
    # 如果可达，筛掉到达目的地的最后一跳
    if res_2:
        res_1.pop()
    # 转成C类地址
    for item in res_1:
        temp.append((item[0], re.sub("\d+$", "0", item[1])))
    res_1 = temp
    
    return res_1


'''
    获取某个城市原始路径特征并写入文件
'''
def get_raw_city_path_feature(city):
    raw_city_path_feature = {}
    count = 0
    with open("./ip/{}{}.txt".format(city,"训练"), "r") as f1:
        print("开始提取{}路径特征......".format(city))
        while True:
            line = f1.readline().strip("\n")
            if line == "":
                break
            res_1 = get_path_feature(line)
            # if res_2 != True:
            #     unreach_count += 1
            # 统计路径特征
            for feature in res_1:
                if feature in raw_city_path_feature.keys():
                    raw_city_path_feature[feature] += 1
                else:
                    raw_city_path_feature[feature] = 1
            count += 1
            print(count)
    with open("./ip/{}{}.txt".format(city,"原始路径特征"), "w+") as f:
        f.write(str(raw_city_path_feature))



'''
    三元组<跳数，路由器IP，概率>
    cities是所有城市（广州、西安、长沙）
'''
def get_city_path_feature(cities):
    hop_base = {}
    # 统计每一跳的基数
    for city in cities:
        with open("./ip/{}{}.txt".format(city,"原始路径特征"), "r") as f1:
            # 字符串转为字典
            raw_city_path_feature = eval(f1.readline().strip("\n"))
            # 不同路径特征加入，跳数相同就应该算作基数
            for key,value in raw_city_path_feature.items():
                if key[0] in hop_base.keys():
                    hop_base[key[0]] += value
                else:
                    hop_base[key[0]] = value
    print(hop_base)
    # 计算路径特征三元组中的概率，并写入文件中
    for city in cities:
        with open("./ip/{}{}.txt".format(city,"原始路径特征"), "r") as f1:
            city_path_feature = {}
            # 字符串转为字典
            raw_city_path_feature = eval(f1.readline().strip("\n"))
        for key, value in raw_city_path_feature.items():    
            city_path_feature[key] = round(value / hop_base[key[0]], 3)
        # 将路径特征写入字典
        f2 = open("./ip/{}{}.txt".format(city,"路径特征"), "w+")
        f2.write(str(city_path_feature))
        f2.close()


'''
    通过路径特征匹配得到概率，并确定IP最可能的定位区域
    cities是候选定位区域
'''
def get_ip_location(ip, cities):
    # 获取目标IP路径特征，类型为list
    ip_path_feature = get_path_feature(ip)
    # 获取城市路径特征
    cities_path_feature = [] 
    for city in cities:
        with open("./ip/{}{}.txt".format(city,"路径特征"), "r") as f1:
            cities_path_feature.append(eval(f1.readline().strip("\n")))
    # 计算概率
    location_p = []
    for city_path_feature in cities_path_feature:
        p = 0
        temp = []
        for item in ip_path_feature:
            if item in city_path_feature.keys():
                p += city_path_feature[item]
                temp.append(city_path_feature)
            # print("目标IP路径特征\t",ip_path_feature)
        location_p.append(round(p, 3))
    # 比较概率相对大小，选择概率最大的城市作为定位结果
    location = cities[location_p.index(max(location_p))]

    return location_p, location       

    



    
