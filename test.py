from get_ip_feature import get_raw_city_path_feature, get_city_path_feature, get_ip_location


if __name__ == "__main__":
    # 获取城市的路径特征，原本是西安 广州 长沙，将广州换为南京试试
    cities = ["南京","长沙","西安"]
    for city in cities:
        get_raw_city_path_feature(city)
        print("{}路径特征提取完成！".format(city))
    get_city_path_feature(cities)
    print("所有区域路径特征提取完成！")

    # 测试计算概率，并写入文件
    for city in cities:
        with open("./ip/{}{}.txt".format(city,"测试"), "r") as f1:
            f2 = open("./ip/{}{}.txt".format(city,"定位结果"), "w+")
            count = 0
            print("测试位于{}的目标IP......".format(city))
            while True:
                ip = f1.readline().strip("\n")
                if ip == "":
                    break
                location_p, location = get_ip_location(ip, cities)
                f2.write(str(ip) + "  " + str(location_p) + "  " + str(location) + "\n")
                count += 1
                print(count)
            f2.close()
        print("测试位于{}的目标IP已完成。".format(city))
