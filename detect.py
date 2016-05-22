# -*- coding: utf-8 -*-

import os
import logging
import cv2

from config import *


log = logging.getLogger('detect').debug

cascades = {
    'face': 'cascades/haarcascade_frontalface_alt.xml',
    'eye': 'cascades/haarcascade_eye.xml',
    'mouth': 'cascades/haarcascade_mcs_mouth.xml',
    'nose': 'cascades/haarcascade_mcs_nose.xml',
}


def resize_overlay(overlay_path, feature_width, scale):
    """
    make overlay size to feature size and scale after
    """
    overlay = cv2.imread(overlay_path)
    overlay_height, overlay_width, channels = overlay.shape

    ratio = float(feature_width) / overlay_width
    width = int(overlay_width * ratio * scale)
    height = int(overlay_height * ratio * scale)

    result = cv2.resize(overlay, (width, height), interpolation=cv2.INTER_AREA)

    log('resize overlay - %s: width=%s height=%s', overlay_path, width, height)
    return result


def make_overlay(image_path, overlay_path, x, y, width, height, position=POSITION_CENTER, scale=1.0):
    overlay_resized = resize_overlay(overlay_path, width, scale)
    overlay_height, overlay_width, channels = overlay_resized.shape
    offset = int((width - width * scale) / 2)

    # POSITION_CENTER by default
    roi_x = x + offset
    roi_y = y + (height - overlay_height) / 2

    if position == POSITION_UPPER_TOP:
        roi_x = x + offset
        roi_y = y - overlay_height

    elif position == POSITION_TOP:
        roi_x = x + offset
        roi_y = y

    elif position == POSITION_BOTTOM:
        roi_x = x + offset
        roi_y = y + height - overlay_height

    elif position == POSITION_LOWER_BOTTOM:
        roi_x = x + offset
        roi_y = y + height

    elif position == POSITION_LEFT:
        roi_x = x - overlay_width
        roi_y = y + (height - overlay_height) / 2

    elif position == POSITION_RIGHT:
        roi_x = x + width
        roi_y = y + (height - overlay_height) / 2

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


def detect_persons(image_path):
    result = []

    image = cv2.imread(image_path)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_list = detect_feature('face', image_gray)

    for x, y, width, height in face_list:
        roi = image_gray[y:y+height, x:x+width]

        result.append({
            'face': (x, y, width, height),
            'eye': detect_feature('eye', roi, x, y),
            'nose': detect_feature('nose', roi, x, y),
            'mouth': detect_feature('mouth', roi, x, y),
        })

    log('detect persons: count=%s', len(result))
    return result


