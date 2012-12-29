import Image, ImageChops, ImageOps
import math
import numpy as np
import matplotlib.pyplot as plt

# the number of the correct image in each set (set number = index + 1)
result = [19, 20, 8, 22, 6, 23, 12, 15, 5, 29, 28, 18, 12, 25, 8, 6, 15, 24, 15, 29, 22, 20]

def image_entropy(img):
	"""calculate the entropy of an image"""
	histogram = img.histogram()
	histogram_length = sum(histogram)
	samples_probability = [float(h) / histogram_length for h in histogram]
	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

def load (imgset):
	imgs = []
	for i in range(1, 31):
		imgs.append(Image.open('set-%s/%i.jpg' % (imgset, i)))
	return imgs

def avgentropy(imgset, imgs):
	idxs = range(0, 30)
	entropies = []
	# precalculate all entropies
	for i in range(0, 29):
		diff = ImageChops.difference(imgs[i], imgs[i+1])
		entropies.append(image_entropy(diff))
	print entropies

	avg = []
	# average of the entropy of the difference with previous & next images.
	avg.append(entropies[0])
	for i in range(1,29):
		avg.append((entropies[i-1] + entropies[i]) / 2.)
		print avg[-1]
	avg.append(entropies[-1])
	#idxs = range(0, 30)
	#OFFSET = 1
	#avg = []
	# compare all images in the specified range
	#for i in idxs:
	#	ent = []
	#	idxs2 = range(max(0, i-OFFSET), min(i+OFFSET+1, 30))
	#	for j in idxs2:
	#		if i != j:
	#			diff = ImageChops.difference(imgs[i], imgs[j])
	#			ent.append(image_entropy(diff))
	#	avg.append(np.mean(ent))
	# save a plot of the average entropy array
	plt.plot(idxs, avg, 'bo-')
	plt.axvline(result[imgset-1]-1, color="r")
	plt.savefig("avg-%i-%i.png" % (imgset, len(idxs)))
	plt.clf()
	return avg

def findorig (avg):
	# find the peak for the original image
	orig = -1
	for i in range(1, len(avg) - 1):
		if avg[i-1] + 0.1 < avg[i] and avg[i] > avg[i+1] + 0.1:
			orig = i+1
	# if no peak found, assume image 29 is the original.
	# this could technically also be image 2, I guess, but I haven't seen any
	# samples where the original image is at position 2.
	if orig == -1:
		orig = 29
	return orig

def singleset (imgset):
	imgs = load(imgset)
	avg = avgentropy(imgset, imgs)
	orig = findorig(avg)
	print "Guess:", orig
	return orig == result[imgset-1]

def allsets ():
	correct = 0
	for imgset in range(1, len(result) + 1):
		if singleset(imgset):
			print "Set %i correct!" % imgset
			correct += 1
	print "Total correct: %f %%" % (correct * 100. / len(result))

if __name__ == "__main__":
	import sys
	if len(sys.argv) == 2:
		imgset = int(sys.argv[1])
		if singleset(imgset):
			print "Set %i correct!" % imgset
		else:
			print "Set %i incorrect!" % imgset
	else:
		allsets()

