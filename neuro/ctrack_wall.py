from collections import namedtuple as nt
import argparse

import cv2
import numpy as np

class BGR:
    black = (0,0,0)
    grey = (128, 128, 128)

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

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
	# 'wall': hsv_cls.grey,
}

class ExtractFeatures:
	
	def __init__(self):
		self.img = None
		self.hsv_img = None
		self.img_dim = None

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


	def process_contour(self, ctr, obj):
		# Fixed horizontal rectangler
		res = []
		for c in ctr:
			x,y,w,h = cv2.boundingRect(c)
			cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
			# Normalize bbox to be between 0 and 1
			res.append([
				x/self.img_dim[0], y/self.img_dim[1],
				w/self.img_dim[0], h/self.img_dim[1],
				# 0 if obj=='goal' else 1
				])
		return res

	def run(self, img):
		setattr(self, 'img', img)
		setattr(self, 'hsv_img', cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV))
		setattr(self, 'img_dim', img.shape)

		features = []
		for obj, hsv_clr in objects.items():
			ctr, hier = self.get_contour(hsv_clr)
			if ctr is None:
				continue
			coords = self.process_contour(ctr, obj)
			for i in coords:
				features.append(i)
		min_feats = 1
		if len(features)<min_feats:
			for i in range(min_feats-len(features)):
				features.append([0,0,0,0])
		fmt_features = ','.join([str(item) for sublist in features for item in sublist])
		print(fmt_features)
		return features

class Pipeline:
	def __init__(self, mode='photo', fpath=None, display=False):
		self.mode = mode
		self.fpath = fpath
		self.display = display

	def run(self):
		ef = ExtractFeatures()

		if self.mode == 'photo':
			img = cv2.imread(self.fpath)
			# print(img.shape)
			features = ef.run(img)
			if self.display:
				resize = ResizeWithAspectRatio(ef.img, width=560) # Resize by width OR
				cv2.imshow("img", resize)
				cv2.waitKey(30000)
				cv2.destroyAllWindows()

		else: # Video
			video = cv2.VideoCapture(self.fpath)
			while True:
				ret, img=video.read()
				features = ef.run(img)
				if self.display:
					cv2.imshow("img", ef.img)
				cv2.waitKey(10)
			cv2.destroyAllWindows()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Process input args')
	parser.add_argument('mode', type=str, nargs='+',
						help='Input video or photo mode')
	parser.add_argument('path', type=str, nargs='+',
						help='Input filepath')
	args = parser.parse_args().__dict__
	pipeline = Pipeline(args['mode'][0], fpath=args['path'][0])
	pipeline.run()
