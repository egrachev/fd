# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import cv2
import glob

from datetime import datetime
from pony.orm import *
from config import *
from detect import detect_persons

db = Database()


class User(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')

    first_name = Required(unicode)
    last_name = Required(unicode)
    username = Required(unicode)

    sessions = Set('Session')


class Photo(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')

    width = Required(int)
    height = Required(int)

    file_origin = Required(unicode)
    file_path = Optional(unicode)
    file_id = Required(unicode)

    session = Required('Session')


STATUS_OPEN = 0
STATUS_CLOSE = 1
STATUS_CURRENT = 2


class Session(db.Entity):
    date_create = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    name = Required(unicode, unique=True)

    chat_id = Required(int)
    status = Required(int)

    photo = Optional('Photo')
    user = Required('User')
    features = Set('Feature')


class Overlay(db.Entity):
    name = Required(unicode)
    image = Required(unicode)

    width = Required(int)
    height = Required(int)

    type = Required('FeatureType')
    feature_overlay_list = Set('FeatureOverlay')


class FeatureType(db.Entity):
    name = Required(unicode)
    color = Required(unicode)

    features = Set('Feature')
    overlays = Set('Overlay')


class Feature(db.Entity):
    x1 = Required(int)
    y1 = Required(int)

    x2 = Required(int)
    y2 = Required(int)

    width = Required(int)
    height = Required(int)

    type = Required('FeatureType')
    session = Required('Session')
    parent = Optional('Feature', reverse='children')
    children = Set('Feature', reverse='parent')
    feature_overlay_list = Set('FeatureOverlay')


class FeatureOverlay(db.Entity):
    feature = Required('Feature')
    overlay = Required('Overlay')


db.bind('postgres', user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME)
db.generate_mapping(create_tables=True)


@db_session
def initial_data():
    if not FeatureType.exists():
        feature_types = {
            'face': FeatureType(name='face', color='255,0,0'),
            'eye': FeatureType(name='eye', color='0,255,0'),
            'nose': FeatureType(name='nose', color='0,255,255'),
            'mouth': FeatureType(name='mouth', color='0,0,255'),
        }
    else:
        feature_types = {
            'face': FeatureType.get(name='face', color='255,0,0'),
            'eye': FeatureType.get(name='eye', color='0,255,0'),
            'nose': FeatureType.get(name='nose', color='0,255,255'),
            'mouth': FeatureType.get(name='mouth', color='0,0,255'),
        }

    for overlay_path in glob.glob('overlays/*/*.*'):
        if not Overlay.get(image=overlay_path):
            _, type_name, filename = overlay_path.split('/')
            name, extension = filename.split('.')

            overlay_image = cv2.imread(overlay_path)
            height, width, channels = overlay_image.shape

            Overlay(
                type=feature_types[type_name],
                name=name,
                image=overlay_path,
                width=width,
                height=height
            )


initial_data()


@db_session
def create_feature(params, feature_type, photo, parent=None):
    x, y, width, height = map(int, params)

    return Feature(
        photo=photo, type=feature_type,
        x1=x, y1=y, x2=x + width, y2=y + height,
        width=width, height=height,
        parent=parent,
    )


@db_session
def create_overlay(photo_id, overlay):
    photo = Photo[photo_id]
    overlay_dir, overlay_name = overlay.split('/')
    overlay_path = os.path.join(OVERLAYS_DIR, overlay)

    overlay_image = cv2.imread(overlay_path)
    height, width, channels = overlay_image.shape

    if overlay_dir == 'face':
        overlay_type = TYPE_FACE
    elif overlay_dir == 'eyes':
        overlay_type = TYPE_EYE
    elif overlay_dir == 'noses':
        overlay_type = TYPE_NOSE
    elif overlay_dir == 'mouths':
        overlay_type = TYPE_MOUTH
    else:
        overlay_type = TYPE_UNKNOWN

    Overlay(
        photo=photo,
        type=overlay_type,
        name=overlay_name,
        image=overlay_path,
        width=width,
        height=height
    )


@db_session
def photo_exists(file_id):
    return Photo.exists(file_id=file_id)


@db_session
def get_feature(feature_id):
    return Feature[feature_id]


@db_session
def get_features(photo_id):
    return list(select(f for f in Feature if f.photo == Photo[photo_id]))


@db_session
def create_photo(photo_path, width, height, file_id):
    session = Session.get(status=STATUS_CURRENT)

    photo = Photo(
        width=width,
        height=height,
        file_origin=photo_path,
        file_id=file_id,
    )

    session.photo = photo

    for person in detect_persons(photo_path):
        parent = create_feature(person['face'], TYPE_FACE, photo)

        for eye in person['eyes']:
            create_feature(eye, TYPE_EYE, photo, parent=parent)

        for nose in person['noses']:
            create_feature(nose, TYPE_NOSE, photo, parent=parent)

        for mouth in person['mouths']:
            create_feature(mouth, TYPE_MOUTH, photo, parent=parent)


@db_session
def get_user_id(first_name, last_name):
    user = User.get(first_name=first_name, last_name=last_name)

    if user:
        return user.id


@db_session
def create_user(first_name, last_name, username):
    if not User.get(first_name=first_name, last_name=last_name):
        User(
            first_name=first_name,
            last_name=last_name,
            username=username,
        )


# session

@db_session
def create_session(name, chat_id, user_id):
    user = User[user_id]

    for s in Session.select(lambda s: s.user == user):
        s.status = STATUS_OPEN

    Session(name=name, user=user, chat_id=chat_id, status=STATUS_CURRENT)


@db_session
def use_session(user_id, session_id):
    user = User[user_id]

    for s in Session.select(lambda s: s.user == user):
        s.status = STATUS_OPEN

    Session[session_id].status = STATUS_CURRENT


@db_session
def close_session(chat_id, user):
    session = Session.get(chat_id=chat_id, user=user)
    session.status = STATUS_CLOSE


@db_session
def get_file_origin(photo_id):
    return Photo[photo_id].file_origin


@db_session
def get_current_photo_id():
    session_id = get_current_session_id()

    if Session[session_id].photo:
        return Session[session_id].photo.id


@db_session
def get_session_name(session_id):
    return Session[session_id].name


@db_session
def get_current_session_id():
    return Session.get(status=STATUS_CURRENT).id


@db_session
def get_session_by_name(name):
    return Session.get(name=name).id


@db_session
def get_session_list(user_id):
    return list(select(s for s in Session if s.user == User[user_id]))
