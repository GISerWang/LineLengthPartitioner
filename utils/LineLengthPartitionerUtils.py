# -*- coding: utf-8 -*-
from beans.LineInfo import LineInfo
from shapely.geometry import LineString
from shapely.ops import substring
# 将MultiLineString转换成LineString
def MultiLineString2LineString(gdf,params):
    lineInfoArr = []
    for index, row in gdf.iterrows():
        if row[params['geometryField']].type == 'MultiLineString':
            # row[params['geometryField']].geoms：获得MultiLineString中的每一个LineString
            for geom in row[params['geometryField']].geoms:
                # row[params['idField']]表示源数据中的唯一标识
                lineInfoArr.append(LineInfo(row[params['idField']], geom))
        if row[params['geometryField']].type == 'LineString':
            lineInfoArr.append(LineInfo(row[params['idField']], row[params['geometryField']]))
    return lineInfoArr
# 判断点target是否处于pts-pte这条线上
def isBetween(pts,pte,target):
    if (target.x > pts[0] and target.x > pte[0]) or (target.x < pts[0] and target.x < pte[0]):
        return False
    if (target.y > pts[1] and target.y > pte[1]) or (target.y < pts[1] and target.y < pte[1]):
        return False
    return True
# 判断pt是否为交叉点
def isCrossPoint(pt,cpts):
    for cpt in cpts:
        if cpt.x == pt[0] and cpt.y == pt[1]:
            return True
    return False
def lineSplit(lineInfo,cpSegment,meters):
    if LineString(cpSegment).length == 0:
        return
    remainLength = LineString(cpSegment).length
    startLen = 0
    while remainLength >= meters:
        segment = substring(LineString(cpSegment), startLen, startLen+meters)
        lineInfo.addSegment(segment)
        remainLength = remainLength - meters
        startLen = startLen + meters
    segment = substring(LineString(cpSegment), startLen, startLen + meters)
    lineInfo.addSegment(segment)

# 将线段按照meters距离进行分割
def split(lineInfo,meters):
    # lineInfo所有的点序列
    lineCoordArr = list(lineInfo.lineString.coords)
    # 用于临时存储交叉点
    i = 0
    while i < len(lineCoordArr)-1:
        for j in range(len(lineInfo.tempCrossPoints)):
            if isBetween(lineCoordArr[i], lineCoordArr[i+1], lineInfo.tempCrossPoints[j]):
                lineCoordArr.insert(i+1, (lineInfo.tempCrossPoints[j].x,lineInfo.tempCrossPoints[j].y))
                # 如果不i--，会有小概率出现bug
                # 例如以下情况，外层是 1 2 4 5 6，交点是4 3（无序的），i==1的时候会2的位置先插入4，则外层变为1 2 4 4 5 6
                # 下一轮外层的i自增1，变i==2，从索引i==2 时会从4开始向后搜索，导致交点3 无法插入
                del lineInfo.tempCrossPoints[j]
                i = i -1
                break
        i = i + 1
    while i < len(lineCoordArr) - 1:
        if lineCoordArr[i][0] == lineCoordArr[i+1][0] and lineCoordArr[i][1] == lineCoordArr[i+1][1]:
            del lineCoordArr[i]
            i = i - 1
        i = i + 1
    index = 0
    lineInfo.addCpSegmentArr()
    lineInfo.addCpSegmentElement(index,lineCoordArr[0])
    for i in range(1,len(lineCoordArr)):
        if isCrossPoint(lineCoordArr[i],lineInfo.crossPoints):
            lineInfo.addCpSegmentElement(index, lineCoordArr[i])
            index = index+1
            if i < len(lineCoordArr) - 1:
                lineInfo.addCpSegmentArr()
                lineInfo.addCpSegmentElement(index, lineCoordArr[i])
        else:
            lineInfo.addCpSegmentElement(index, lineCoordArr[i])
    for cpSegment in lineInfo.getCpSegments():
        lineSplit(lineInfo,cpSegment,meters)


# 线段分割的主函数
def Process(lineInfoArr,params):
    # 求LineString的相交点位
    for i in range(len(lineInfoArr)):
        for j in range(len(lineInfoArr)):
            if lineInfoArr[j].id == lineInfoArr[i].id:
                continue
            if lineInfoArr[j].lineString.intersects(lineInfoArr[i].lineString):
                # cp表示交点，如果存在两个交点类型为MultiPoint
                cp = lineInfoArr[j].lineString.intersection(lineInfoArr[i].lineString)
                if cp.type == 'Point':
                    lineInfoArr[i].addCrossPoint(cp)
                if cp.type == 'MultiPoint':
                    for geom in cp:
                        lineInfoArr[i].addCrossPoint(geom)
        split(lineInfoArr[i],params["meters"])