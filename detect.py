# -*- coding: utf-8 -*-

import os
import logging
import cv2

from config import *
from db import *

log = logging.getLogger('detect').debug

cascades = {
    'face': 'cascades/haarcascade_frontalface_alt.xml',
    'eye': 'cascades/haarcascade_eye.xml',
    'mouth': 'cascades/haarcascade_mcs_mouth.xml',
    'nose': 'cascades/haarcascade_mcs_nose.xml',
}

COLOR_FACE = 255, 0, 0
COLOR_EYE = 0, 255, 0
COLOR_NOSE = 0, 255, 255
COLOR_MONTH = 0, 0, 255

FEATURE_SCALE = 1.3
FEATURE_MIN_NEIGHBORS = 10


def resize_overlay(overlay_path, width):
    overlay = cv2.imread(overlay_path)
    overlay_height, overlay_width, channels = overlay.shape

    ratio = float(width) / overlay_width
    height = overlay_height * ratio

    result = cv2.resize(overlay, (width, height), interpolation=cv2.INTER_AREA)

    log('resize overlay - %s: width=%s height=%s', overlay_path, width, height)
    return result


def make_overlay(image_path, overlay_path, x, y, width, height):
    overlay_resized = resize_overlay(overlay_path, width)
    overlay_height, overlay_width, channels = overlay_resized.shape

    # center
    roi_x = x + abs(width - overlay_width) / 2
    # roi_y1 = y + abs(height - overlay_height) / 2
    roi_y = y + height - overlay_height

    image = cv2.imread(image_path)
    roi = image[roi_y:roi_y + overlay_height, roi_x:roi_x + overlay_width]

    # Now create a mask of logo and create its inverse mask also
    overlay_gray = cv2.cvtColor(overlay_resized, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(overlay_gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Now black-out the area of logo in ROI
    image_bg = cv2.bitwise_and(roi, roi, mask=mask)

    # Take only region of logo from logo image.
    overlay_fg = cv2.bitwise_and(overlay_resized, overlay_resized, mask=mask_inv)

    # Put logo in ROI and modify the main image
    image[roi_y:roi_y + overlay_height, roi_x:roi_x + overlay_width] = cv2.add(image_bg, overlay_fg)

    log('make overlay - %s: x=%s y=%s width=%s height=%s', overlay_path, roi_x, roi_y, overlay_width, overlay_height)
    return image


def draw_rect(image, x, y, width, height, color=(0, 0, 0), thickness=2):
    log('draw rectangle: x=%s y=%s width=%s height=%s', x, y, width, height)
    cv2.rectangle(image, (x, y), (x+width, y+height), color, thickness)


def detect_feature(name, image, rel_x=0, rel_y=0):
    result = []

    cascade = cv2.CascadeClassifier(cascades[name])
    feature_list = cascade.detectMultiScale(image, FEATURE_SCALE, FEATURE_MIN_NEIGHBORS)

    for feature in feature_list:
        x, y, width, height = feature

        if rel_x or rel_y:
            x += rel_x
            y += rel_y

        result.append(
            (x, y, width, height)
        )

        log('detect feature - %s: x=%s y=%s width=%s height=%s', name, x, y, width, height)

    return result


def detect_persons(image):
    persons = []

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_list = detect_feature('face', image_gray)

    for x, y, width, height in face_list:
        roi = image_gray[y:y+height, x:x+width]

        persons.append({
            'face': (x, y, width, height),
            'eyes': detect_feature('eye', roi, x, y),
            'noses': detect_feature('nose', roi, x, y),
            'mouths': detect_feature('mouth', roi, x, y),
        })

    log('detect persons: count=%s', len(persons))
    return persons

# img = cv2.imread(os.path.join(USER_IMAGES_DIR, 'test1.jpg'))
# person_list = detect_persons(img)
# p = person_list[0]
# overlay_img = cv2.imread(os.path.join(OVERLAYS_NOSES_DIR, 'mustache.png'))
# p.draw_nose(img, overlay_img)
#
# cv2.namedWindow('img', cv2.WINDOW_NORMAL)
# cv2.imshow('img', img)
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
