## IPLocation

基于路径特征的目标IP区域估计

## 代码结构

|--IPLocation

|----/ip 记录地标IP、目标IP、路径特征以及最终定位结果
|----cz.txt 纯真数据库记录
|----select_from_cz.py 完成地标IP和目标IP的选取
|----get_ip_feature.py 生成对应的区域路径特征和目标IP特征
|----test.py 定位测试

## 依赖包

requests, random, json, re, time

## 使用

地标IP和目标IP已经选取完毕，直接运行test.py即可生成定位结果，定位结果在ip文件夹下查看。整个程序运行时间较长。
