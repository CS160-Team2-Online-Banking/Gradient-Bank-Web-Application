""" # until this is complete, this file should remain commented out
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np


def get_bottom_line(rects):
    buckets = list()
    for rect in rects:
        match_found = False
        rect_min = rect[1]
        rect_max = rect[1] + rect[3]
        for i, bucket in enumerate(buckets):  # check the buckets
            bucket_min = bucket[0]
            bucket_max = bucket[1]
            if rect_min < bucket_max and rect_max > bucket_min:
                buckets[i][0] = min(rect_min, bucket[0])
                buckets[i][1] = max(rect_max, bucket[1])
                buckets[i][2].append(rect)
                match_found = True
                break
        if not match_found:  # add a new bucket if we couldn't find one
            new_bucket = [rect_min, rect_max, [rect]]
            buckets.append(new_bucket)

    sorted_buckets = sorted(buckets, key=(lambda x: x[0]), reverse=True)
    return sorted_buckets[0]


def get_micr_img(check_img):
    # we will operate under the assmuption that the micr is the last clear thing
    # on the check
    # and the check is oriented relatively level with the camera
    s = check_img.shape
    micr_img = check_img[int(s[0] * 0.80):s[0], 0:s[1]]

    ret, thresh = cv2.threshold(micr_img, 50, 255, 0)
    ret, thresh2 = cv2.threshold(micr_img, 127, 255, 0)
    cnts, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    bounding_rects = [cv2.boundingRect(c) for c in cnts]
    bounding_rects = list(filter((lambda x: x[0] and x[1]), bounding_rects))
    bottom_line = get_bottom_line(bounding_rects)
    left = min(map(lambda x: x[0], bottom_line[2])) - 20
    right = max(map(lambda x: x[0] + x[2], bottom_line[2])) + 20
    top = bottom_line[0] - 5
    bottom = bottom_line[1] + 5
    micr_img = thresh[top:bottom, left:right]
    return micr_img
"""