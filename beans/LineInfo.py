class LineInfo():
    def __init__(self,id, lineString):
        self.id = id
        self.lineString = lineString
        self.segments = []
        # List<Geometry>
        self.crossPoints = []
        self.tempCrossPoints = []
        # 经过交叉点分割的线段
        self.cpSegments = []
    def addCrossPoint(self,pt):
        self.crossPoints.append(pt)
        self.tempCrossPoints.append(pt)
    def addCpSegmentArr(self):
        self.cpSegments.append([])
    def addCpSegmentElement(self,idx,pt):
        self.cpSegments[idx].append(pt)
    def getCpSegments(self):
        return self.cpSegments
    def addSegment(self,segment):
        self.segments.append(segment)
    def getSegment(self,):
        return self.segments
