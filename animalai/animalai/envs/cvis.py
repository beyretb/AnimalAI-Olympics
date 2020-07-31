## CVIS for training
from collections import namedtuple as nt
from collections import OrderedDict as OD
import argparse
import matplotlib.pyplot as plt

import cv2
import numpy as np


class HSV:
	"""Color lower and upper bounds in HSV format"""

	@classmethod
	def __getattribute__(cls,attr):
		return [np.array(i) for i in getattr(cls, attr)]

	green = [[33,80,40], [102,255,255]]
	red = [[125,16,88], [179,255,255]]
	grey = [[0,0,0], [0,0,224]]
	brown = [[7,53,40], [18,87,121]]

hsv_cls = HSV()
objects = OD()
objects['goal'] =  hsv_cls.green
# objects['danger_zone'] = hsv_cls.red
# objects['wall'] = hsv_cls.grey

class ExtractFeatures:
	
	def __init__(self, display=True, training=True):
		self.img = None
		self.hsv_img = None
		self.img_dim = None
		self.display = display
		self.training = training

	def get_contour(self, hsv):
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
				cv2.imwrite("/Users/ludo/Desktop/bam.png", self.img)
			# Normalize bbox to be between 0 and 1
			res.append([
				x/self.img_dim[0], y/self.img_dim[1],
				w/self.img_dim[0], h/self.img_dim[1],
				# 0 if obj=='goal' else 1
				])
		return res

	def run(self, img, mode='octx'):
		if not self.training:
			return self.run_test(img)

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

		# Flatten list
		if mode=='gtg':
			idx = 1
		elif mode == 'octx':
			idx = 2
		else:
			idx = 5
		features = features[:idx]
		features = [item for sublist in features for item in sublist]
		return features

	def run_test(self, img):
		"""Returns list of tuples"""
		self.img = (img*255)[:,:,::-1].astype(np.uint8)
		self.hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
		self.img_dim = self.img.shape
		features = []
		for obj_type, hsv_clr in objects.items():
			ctr, hier = self.get_contour(hsv_clr)
			if ctr is None:
				continue
			coords = self.process_contour(ctr, obj_type)
			for box in coords:
				features.append((box, obj_type))
		return features

