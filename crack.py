#!/usr/bin/env python -u
""" Crack a minteye captcha.

python crack.py BASE_CAPTCHA_URL

This process will download all images in the captcha set to disk 
to "./set-X/*.jpg" & the guess for the original image to "./X.jpg".

How does it work?
"""

import os, shutil, urllib2, math, Image, ImageChops
import numpy as np
import matplotlib.pyplot as plt

def next_set_id ():
	""" Funky oneliner to get the next set id based on dir names. """
	return max(map(lambda x: int(x[4:]), filter(lambda x : x.startswith("set-"), os.listdir('./')))) + 1

def download (set_id, base_url):
	os.mkdir('./set-%i' % set_id)
	images = []
	for i in range(1, 31):
		print "Fetching image %i/30" % i
		# TODO: is there an option to do this without extra reading?
		stream = urllib2.urlopen(base_url + "%i" % i)
		f = open('set-%i/%i.jpg' % (set_id, i),'wb')
		f.write(stream.read())
		f.close()
		f = open('set-%i/%i.jpg' % (set_id, i),'r')
		img = Image.open(f)
		img.load()
		f.close()
		images.append(img)
	print "Download finished."
	return images

def image_entropy(img):
	"""calculate the entropy of an image"""
	histogram = img.histogram()
	histogram_length = sum(histogram)
	samples_probability = [float(h) / histogram_length for h in histogram]
	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

def avgentropy(imgset, imgs):
	entropies = []
	# precalculate all entropies
	for i in range(0, 29):
		diff = ImageChops.difference(imgs[i], imgs[i+1])
		entropies.append(image_entropy(diff))

	avg = []
	# average of the entropy of the difference with previous & next images.
	avg.append(entropies[0])
	for i in range(1,29):
		avg.append((entropies[i-1] + entropies[i]) / 2.)
	avg.append(entropies[-1])

	# save a plot of the average entropy array
	plt.plot(range(0, 30), avg, 'bo-')
	plt.savefig("avg-%i.png" % (imgset))
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

def crack (set_id, images):
	print "Calculating average entropy for images"
	avg = avgentropy(set_id, images)
	print "Find the original image peak"
	orig = findorig(avg)
	shutil.copyfile("set-%i/%i.jpg" % (set_id, orig), "%i.jpg" % set_id)
	print 'Original image: %i' % orig

if __name__ == "__main__":
	import sys
	if len(sys.argv) != 2:
		print 'Missing base url argument!'
	base_url = sys.argv[1]
	
	set_id = next_set_id()
	print "Download set with set id", set_id
	images = download(set_id, base_url)
	print "Start cracking..."
	crack(set_id, images)

