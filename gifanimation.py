from images2gif import writeGif
from PIL import Image, ImageDraw
import os
import sys
import random
import argparse
import webbrowser

filename = ""


def makeimages():
    # Create the dir for generated images
    if not os.path.exists("Images"):
        os.makedirs("Images")
    for z in range(1, 31):
        dims = (3507, 2480)  # size of image
        img = Image.new('RGB', dims)  # crete new image
        draw = ImageDraw.Draw(img)
        r = int(min(*dims)/100)
        print "Image img%d.png has been created" % z

        n = 1000

        for i in range(n):
            x, y = random.randint(0, dims[0]-r), random.randint(0, dims[1]-r)
            fill = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.ellipse((x-r, y-r, x+r, y+r), fill)

        img.save('Images/.img%d.png' % z)

def makeAnimatedGif():
    # Recursively list image files and store them in a variable
    path = "./Images/"
    os.chdir(path)
    imgFiles = sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))

    # Grab the images and open them all for editing
    images = [Image.open(fn) for fn in imgFiles]

    global filename
    filename = filename + ".gif"
    writeGif(filename, images, duration=0.2)
    print os.path.realpath(filename)
    print "%s has been created, I will now attempt to open your" % filename
    print "default web browser to show the finished animated gif."
    #webbrowser.open('file://' + os.path.realpath(filename))


def start():
    print "This program will create an animated gif image from the 30 images provided."
    print "Please enter the name for the animated gif that will be created."
    global filename
    filename = raw_input("Do Not Use File Extension >> ")
    print "Please wait while I create the images......"
    makeimages()
    print "Creating animated gif...."
    makeAnimatedGif()

start()