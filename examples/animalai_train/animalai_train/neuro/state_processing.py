from collections import namedtuple as nt
import argparse

import cv2
import numpy as np

# Config
class BGR:
    black = (0,0,0)
    grey = (128, 128, 128)


class HSV:
    """Color lower and upper bounds in HSV format"""

    @classmethod
    def __getattribute__(cls,attr):
        return [np.array(i) for i in getattr(cls, attr)]

    green = [[33,80,40], [102,255,255]]
    # red = [[0,181,0], [6,255,255]]
    # red = [[0,184,0], [179,208,217]]
    red = [[125,16,88], [179,255,255]]

    brown = [[7,53,40], [18,87,121]]

hsv_cls = HSV()
objects = {
    'goal': hsv_cls.green,
    # 'danger_zone': hsv_cls.red,
    # 'tool': hsv_cls.brown
}

class FeatureExtractor:
    
    def __init__(self):
        self.img = None
        self.hsv_img = None

    def get_contour(self, hsv):
        # Config
        kernel_open=np.ones((5,5))
        kernel_close=np.ones((20,20))

        # Apply mask to get contour
        mask = cv2.inRange(self.hsv_img, hsv[0], hsv[1])
        mask_open = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel_open)
        mask_close = cv2.morphologyEx(mask_open,cv2.MORPH_CLOSE,kernel_close)
        ctr,hier = cv2.findContours(mask_close.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if not ctr:
            return None, hier
        return ctr, hier

    def draw_contour(self, ctr, obj):
        if obj in ['goal']: # TODO get rid of this hackiness
            # cv2.drawContours(self.img,ctr,0,BGR.black,2)
            return ctr
        else:
            hull = np.zeros((0, 1, 2), np.int32)
            for i in range(len(ctr)):
                hull = np.concatenate((hull, ctr[i]), axis=0)
            hull = cv2.convexHull(hull, False)
            # cv2.drawContours(self.img,[hull],-1,BGR.black,2)
            return [hull]

    def process_contour(self, ctr):
        # Fixed horizontal rectangle
        x,y,w,h = cv2.boundingRect(ctr[0])
        cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
        # Rotated rectangle
        # rect = cv2.minAreaRect(ctr[0])
        # box = cv2.boxPoints(rect)
        # box = np.int0(box)
        # cv2.drawContours(self.img,[box],0,(0,0,255),2)
        # res = {'x':x, 'y':y, 'w':w, 'h':h}
        # return nt('coords', list(res.keys()))(**res)
        res = [x,y,w,h]
        return res

    def run(self, img):
        setattr(self, 'img', (img*255).astype('uint8'))
        setattr(self, 'hsv_img', cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV))


        features = {}
        for obj, hsv_clr in objects.items():
            ctr, hier = self.get_contour(hsv_clr)
            if ctr is None:
                features[obj] = [0,0,0,0]
                continue
            ctr = self.draw_contour(ctr, obj)
            coords = self.process_contour(ctr)
            features[obj] = coords


        return features
