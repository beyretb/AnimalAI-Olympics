from collections import namedtuple as nt
import argparse
import matplotlib.pyplot as plt

import cv2
import numpy as np

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
	grey = [[0,0,0], [0,0,224]]
	brown = [[7,53,40], [18,87,121]]

hsv_cls = HSV()
objects = {
	'goal': hsv_cls.green,
	# 'danger_zone': hsv_cls.red,
	'wall': hsv_cls.grey,
}

class ExtractFeatures:
	
	def __init__(self, display=False, training=True):
		self.img = None
		self.hsv_img = None
		self.img_dim = None
		self.display = display
		self.training = training

	def get_contour(self, hsv):
		# Config

		# Apply mask to get contour
		mask = cv2.inRange(self.hsv_img, hsv[0], hsv[1])
		res = cv2.bitwise_and(self.hsv_img, self.hsv_img, mask=mask)[:,:,2]
		ctr,hier = cv2.findContours(res,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
		if not ctr:
			return None, hier
		return ctr, hier


	def process_contour(self, ctr, obj):
		# Fixed horizontal rectangler
		res = []
		for c in ctr:
			x,y,w,h = cv2.boundingRect(c)
			if self.display:
				cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
			# Normalize bbox to be between 0 and 1
			res.append([
				x/self.img_dim[0], y/self.img_dim[1],
				w/self.img_dim[0], h/self.img_dim[1],
				# 0 if obj=='goal' else 1
				])
		return res

	def run(self, img):
		if self.training:
			img = np.ascontiguousarray(
				cv2.imdecode(np.frombuffer(img, np.uint8), -1))
		# plt.imshow(img)
		setattr(self, 'img', img)
		setattr(self, 'hsv_img', cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV))
		setattr(self, 'img_dim', img.shape)

		features = []
		for obj, hsv_clr in objects.items():
			ctr, hier = self.get_contour(hsv_clr)
			if ctr is None:
				features.append([0,0,0,0])
				continue
			coords = self.process_contour(ctr, obj)
			for i in coords:
				features.append(i)
		# min_feats = 2
		# if len(features)<min_feats:
		# 	for i in range(min_feats-len(features)):
		# 		features.append([0,0,0,0])
		# Flatten list
		features = features[:2]
		features = [item for sublist in features for item in sublist]
		return features



