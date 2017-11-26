import StringIO
import subprocess
import os
import time
import thread
from datetime import datetime
from PIL import Image
from picamera import PiCamera
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import tempfile

# Motion detection settings:
# Threshold (how much a pixel has to change by to be marked as "changed")
# Sensitivity (how many changed pixels before capturing an image)
# ForceCapture (whether to force an image to be captured every forceCaptureTime seconds)
threshold = 10
sensitivity = 20
forceCapture = False
forceCaptureTime = 5 # Every five seconds

# File settings
saveWidth = 1280
saveHeight = 960
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk
camera = PiCamera()
saved_umask = os.umask(0077)

    
# Capture a small test image (for motion detection)
def captureTestImage():
    # Create the in-memory stream
    stream = BytesIO()
    camera.start_preview()
    sleep(1)
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    im = Image.open(stream)
    buffer = im.load()
    return im, buffer

def makeGIF(tempdir, time):
    os.system('convert -delay 10 -loop 0 {}/*.jpg {}-{}-{}-{}-{}-{}.gif'.format(tempdir, time.year, time.month, time.day, time.hour, time.minute, time.second))
    print("MADE GIF")

# Save a full size image to disk
def saveImage(width, height, diskSpaceToReserve):
    tempdir = tempfile.mkdtemp()
    print("saving image")
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    try:
        for i in range(10):
            filename = "capture-{}.jpg".format(i)
            path = os.path.join(tempdir, filename)
            camera.capture(path)
        thread.start_new_thread(makeGIF, (tempdir,time,))
        
    except IOError as e:
        print 'ERROR'
    finally:
        print("DID IT")
    print "Captured %s" % filename

# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(".")):
            if filename.endswith(".jpg") or filename.endswith(".gif"):
                os.remove(filename)
                print "Deleted %s to avoid filling disk" % filename
                if (getFreeSpace() > bytesToReserve):
                    return

# Get available disk space
def getFreeSpace():
    st = os.statvfs(".")
    du = st.f_bavail * st.f_frsize
    return du
        
# Get first image

# Reset last capture time
def main():
    print("IN MAIN")
    lastCapture = time.time()
    image1, buffer1 = captureTestImage()
    while True:

        print("running loop")

        # Get comparison image
        image2, buffer2 = captureTestImage()

    	# Count changed pixels
    	changedPixels = 0
    	for x in xrange(0, 100):
       	    for y in xrange(0, 75):
                print("getting pixel diff")
            	# Just check green channel as it's the highest quality channel
            	pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
            	if pixdiff > threshold:
                    print("motion detected")
                    changedPixels += 1

    	# Check force capture
    	if forceCapture:
            if time.time() - lastCapture > forceCaptureTime:
            	changedPixels = sensitivity + 1
                
    	print("changed pixels {}".format(changedPixels))
    	# Save an image if pixels changed
    	if changedPixels > sensitivity:
            lastCapture = time.time()
            saveImage(saveWidth, saveHeight, diskSpaceToReserve)
    
    	# Swap comparison buffers
   	image1 = image2
    	buffer1 = buffer2
main()
