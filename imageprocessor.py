import math

import cv2
import numpy as np
from PIL import ImageTk, Image
import threading
import csv
import datetime


class Processor(threading.Thread):
    """
    Represents an image processor. Handles image processing operations
    """

    def __init__(self, facade):
        """
        :param facade: Facade instance that connects backend functionality
        """
        threading.Thread.__init__(self)
        self.facade = facade

        self.hsv_low = None
        self.hsv_high = None
        self.rawmask = None
        self.kernal = (5, 5)
        self.similarity = None
        self.logfilename = None
        self.previousedgeindex = None
        # Flags
        self.eroded = False
        self.dilated = False
        self.open = False
        self.close = False
        self.thresh = 10000

        self.daemon = True
        self.start()

    def setlogfilename(self, name):
        self.logfilename = str(name)

    def logdatatofile(self, diff, height, width, status):
        fieldnames = ["Time", "Diff", "Top position", "Horizontal position", "Status"]
        with open('logged_data.csv', "a", newline='') as my_file:
            writer = csv.DictWriter(my_file, fieldnames=fieldnames)
            if my_file.tell() == 0:
                writer.writeheader()
            writer.writerow({"Time": datetime.datetime.now().time().replace(microsecond=0).isoformat(),
                             "Diff": diff,
                             "Top position": height,
                             "Horizontal position": width,
                             "Status": status})

    def get_clean_video_stream(self):
        """
        Converts the frame from BGR to RGB colorspace
        :return: PIL RGB image
        """
        frame = self.facade.getcameraframe()
        # Check if frame is empty. The first few at camera startup will be.
        if np.any(frame):
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(image)
            return self.current_image

    def get_masked_video(self, inverted=False):
        """
        Masks the frame according to hsv and morph
        :param inverted: Flag for inverting mask
        :return: Masked PIL image
        """
        image = self.facade.getcameraframe()
        frame = self.smoothimage(image)
        if self.hsv_low is not None:
            hsvimage = self.converttohsv(frame)
            # rgbimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.rawmask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            if self.eroded:
                self.mask = self.erodemask(self.rawmask)
            if self.dilated:
                self.mask = self.dilatemask(self.rawmask)
            if self.open:
                self.mask = self.openmask(self.rawmask)
            if self.close:
                self.mask = self.closemask(self.rawmask)
            if not self.eroded and not self.dilated and not self.open and not self.close:
                self.mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
            if inverted:
                self.mask = cv2.bitwise_not(self.mask)

            # maskedimg = cv2.bitwise_and(rgbimage, rgbimage, mask=self.mask)
            self.current_image = Image.fromarray(self.mask)
            return self.current_image
        else:
            print("[INFO] Missing HSV mask!")

    def getrawmask(self):
        frame = self.facade.getcameraframe()
        hsvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(hsvimage, self.hsv_low, self.hsv_high)
        return self.mask

    def converttohsv(self, img):
        image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        return image

    def smoothimage(self, img):
        image = cv2.GaussianBlur(img, self.kernal, cv2.BORDER_DEFAULT)
        return image

    def detectblob(self, img):
        detector = cv2.SimpleBlobDetector()
        keypoints = detector.detect(img)
        img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                               cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow("Keypoints", img_with_keypoints)

    # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
    def get_image_diff(self, img1, img2):
        diffimg = np.subtract(img1, img2)
        status = ""
        errorflag = False
        img1extpts = self.getextremepoints(img1)
        img2extpts = self.getextremepoints(img2)

        leftdist = self.getdistancebetweenpoints(img1extpts[0], img2extpts[0])
        rightdist = self.getdistancebetweenpoints(img1extpts[1], img2extpts[1])
        topdist = self.getdistancebetweenpoints(img1extpts[2], img2extpts[2])
        botdist = self.getdistancebetweenpoints(img1extpts[3], img2extpts[3])

        # print("Shifted left by: " + str(leftdiff))
        # print("Shifted right by: " + str(rightdiff))
        # print("Shifted up by: " + str(topdiff))
        # print("Shifted down by: " + str(botdiff))
        # print("Image 1 top x: " + str(img1extpts[2][1]))
        # print("Image 2 top x: " + str(img2extpts[2][1]))
        
        heightdiff = img2extpts[2][1] - img1extpts[2][1]
        print("Height diff: " + str(heightdiff))
        if heightdiff < 1:
            print("Part did not grow")
            status = status + "Part did not grow. "
            errorflag = True

        leftdiff = img2extpts[0][0] - img1extpts[0][0]
        if -3 > leftdiff or leftdiff > 3:
            print("Part moved vertically. Detected on left side")
            status = status + "Vertical shift, Left side. "
            errorflag = True

        rightdiff = img2extpts[1][0] - img1extpts[1][0]
        if -3 > rightdiff or rightdiff > 3:
            print("Part moved vertically. Detected on right side")
            status = status + "Vertical shift, Right side. "
            errorflag = True

        verticallineindex = img2extpts[2][1] + 2
        edgeindex = self.getedgeonline(verticallineindex, img1)
        self.compareedge(edgeindex)
        #height = 720 - img1extpts[2][1]

        self.displaycontours()
        diff = np.count_nonzero(diffimg)
        if not errorflag:
            status = "Normal"
        height = self.heightdiff()
        self.logdatatofile(diff=diff, height=height, width=img1extpts[0][0], status=status)
        return diff

    def heightdiff(self):
        if self.facade.getregisterlength() > 3:
            currentframe = self.facade.getlastimage(-1)
            npreviousframe = self.facade.getlastimage(-4)
            if np.count_nonzero(currentframe) < 4:
                print("Current frame empty")
            if np.count_nonzero(npreviousframe) < 4:
                print("Nth frame empty")
            else:
                currentframepoints = self.getextremepoints(currentframe)
                npreviousframepoints = self.getextremepoints(npreviousframe)
                heightdiff = npreviousframepoints[2][1] - currentframepoints[2][1]
                print("Height diff between curren and fourth last frame: " + str(heightdiff))
                return heightdiff
        else:
            return 0

    def compareedge(self, edgeindex):
        if self.previousedgeindex is None:
            self.previousedgeindex = edgeindex
        else:
            try:
                diffindex = np.subtract(self.previousedgeindex, edgeindex)
                self.previousedgeindex = edgeindex
                print("Diff index: " + str(diffindex))
            except ValueError:
                print("ValueError when comparing edges...")

    def getdistancebetweenpoints(self, pkt1, pkt2):
        dist = math.sqrt((pkt1[0] - pkt2[0]) ** 2 + (pkt1[1] - pkt2[1]) ** 2)
        return dist

    def chechsimilarity(self, img1, img2):
        image1 = np.array(img1)
        image2 = np.array(img2)
        if np.count_nonzero(image1) < 4:
            print("Current frame empty")
        elif np.count_nonzero(image2) < 4:
            print("Last frame empty")
        else:
            self.similarity = self.get_image_diff(image1, image2)
            if self.similarity > self.thresh:
                print("Motion is bigger than threshold. Check printer")
            #print("Nonzeros in diffimg: " + str(self.similarity))

    # TODO: Prøv å bruke det forrige som template...

    # def get_image_diff(self, img1, img2):
    #     image1 = img1
    #     image2 = img2
    #     #diffimg = cv2.subtract(image1, image2)
    #     image1hist = cv2.calcHist([image1], [0], None, [256], [0, 256])
    #     image2hist = cv2.calcHist([image2], [0], None, [256], [0, 256])
    #     diffimg = cv2.matchTemplate(image1hist, image2hist, cv2.TM_CCOEFF_NORMED)[0][0]
    #     diff = 1 - diffimg
    #     #diff = np.count_nonzero(diffimg)
    #     return diff

    def updatehsv(self, hsvlow, hsvhigh):
        self.hsv_low = hsvlow
        self.hsv_high = hsvhigh

    def displaycontours(self):
        mask = self.getrawmask()
        extremepointpos = []
        # contours = self.getcontours(mask)
        frame = np.array(self.facade.getlastimage(-1))
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # contours = np.array(contours).reshape((-1, 1, 2)).astype(np.int32)
        # frame = np.array(self.get_clean_video_stream())

        # frame.resize(frame.shape[0], frame.shape[1], 3)
        for c in contours:
            area = cv2.contourArea(c)
            if area > 100:
                extLeft = tuple(c[c[:, :, 0].argmin()][0])
                extRight = tuple(c[c[:, :, 0].argmax()][0])
                extTop = tuple(c[c[:, :, 1].argmin()][0])
                extBot = tuple(c[c[:, :, 1].argmax()][0])
                #cv2.drawContours(frame, [c], -1, (0, 255, 0), 3)
                #cv2.circle(frame, extLeft, 8, (0, 0, 255), -1)
                #cv2.circle(frame, extRight, 8, (0, 255, 0), -1)
                #cv2.circle(frame, extTop, 8, (255, 0, 0), -1)
                #cv2.circle(frame, extBot, 8, (255, 255, 0), -1)
                extremepointpos = [extLeft, extRight, extTop, extBot]
                # print(extremepointpos)
        #cv2.imshow("Frame", frame)

    def getedgeonline(self, lineindex, frame):
        edgeindex = []
        risingkernel = [1, -1]
        risingedge = np.convolve(frame[lineindex], risingkernel)
        #print(risingedge)
        for index, v in enumerate(risingedge):
            if v == 255 or v == -255:
                #print("Edgeindex: " + str(index))
                edgeindex.append(index)
        #frame[lineindex] = 255
        #cv2.imshow("Section", frame)
        #print(edgeindex)
        return edgeindex

    def getextremepoints(self, img):
        frame = np.array(img)
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = max(contours, key=cv2.contourArea)

        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])
        extremepointpos = [extLeft, extRight, extTop, extBot]

        return extremepointpos

    def getcontours(self, mask):
        _, contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def getcontoursarea(self, mask):
        contours = self.getcontours(mask)
        area = cv2.contourArea(contours)
        return area

    # Morph operations
    def erodemask(self, rawmask):
        mask = cv2.erode(rawmask, self.kernal, iterations=1)
        return mask

    def dilatemask(self, rawmask):
        dilated = cv2.dilate(rawmask, self.kernal, iterations=1)
        return dilated

    def openmask(self, rawmask):
        opened = cv2.morphologyEx(rawmask, cv2.MORPH_OPEN, self.kernal)
        return opened

    def closemask(self, rawmask):
        closed = cv2.morphologyEx(rawmask, cv2.MORPH_CLOSE, self.kernal)
        return closed

    def seterode(self, flag):
        self.eroded = flag

    def setdilate(self, flag):
        self.dilated = flag

    def setopen(self, flag):
        self.open = flag

    def setcolse(self, flag):
        self.close = flag

    def setthresh(self, thresh):
        self.thresh = thresh
