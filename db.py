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

    sessions = Set('Session')


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

    type = Required('FeatureType', lazy=False)
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

    type = Required('FeatureType', lazy=False)
    session = Required('Session')
    parent = Optional('Feature', reverse='children')
    children = Set('Feature', reverse='parent')
    feature_overlay_list = Set('FeatureOverlay')

    def get_color(self):
        return map(int, self.type.color.split(','))


POSITION_UPPER_TOP = 0
POSITION_TOP = 1
POSITION_CENTER = 2
POSITION_BOTTOM = 3
POSITION_LOWER_BOTTOM = 4
POSITION_LEFT = 5
POSITION_RIGHT = 6


class FeatureOverlay(db.Entity):
    feature = Required('Feature')
    overlay = Required('Overlay')
    position = Required(int, default=POSITION_CENTER)
    scale = Required(float, default=1.0)


db.bind('postgres', user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME)
db.generate_mapping(create_tables=True)


@db_session
def initial_data():
    if not FeatureType.exists():
        feature_types = {
            'face': FeatureType(name='face', color='255,0,0'),
            'eye': FeatureType(name='eye', color='0,255,0'),
            'eyes': FeatureType(name='eyes', color='0,0,0'),
            'nose': FeatureType(name='nose', color='0,255,255'),
            'mouth': FeatureType(name='mouth', color='0,0,255'),
        }
    else:
        feature_types = {
            'face': FeatureType.get(name='face', color='255,0,0'),
            'eye': FeatureType.get(name='eye', color='0,255,0'),
            'eyes': FeatureType.get(name='eyes', color='0,0,0'),
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
def create_feature(session, params, feature_type, parent=None):
    x, y, width, height = map(int, params)
    feature = Feature.get(x1=x, y1=y, width=width, height=height)

    if not feature:
        feature = Feature(
            session=session,
            type=feature_type,
            x1=x, y1=y, x2=x + width, y2=y + height,
            width=width, height=height,
            parent=parent,
        )

    return feature


@db_session
def overlay_add(feature_id, overlay_id):
    if not FeatureOverlay.get(feature=Feature[feature_id], overlay=Overlay[overlay_id]):
        FeatureOverlay(
            feature=Feature[feature_id],
            overlay=Overlay[overlay_id],
        )


@db_session
def get_overlay_by_name(name):
    return Overlay.get(name=name)


@db_session
def get_overlays():
    return select(overlay for overlay in Overlay).prefetch(FeatureType)[:]


@db_session
def photo_exists(file_id):
    return Photo.exists(file_id=file_id)


@db_session
def get_feature(feature_id):
    return select(f for f in Feature if f.id == feature_id).prefetch(FeatureType)[:][0]


@db_session
def get_features(user_id):
    session_id = get_current_session_id(user_id)

    return select(f for f in Feature if f.session == Session[session_id]).prefetch(FeatureType)[:]


@db_session
def get_features_overlays(user_id):
    features = get_features(user_id)

    return select(fo for fo in FeatureOverlay if fo.feature in features).prefetch(Feature, Overlay)[:]


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

    persons = detect_persons(photo_path)

    for person in persons:
        parent = create_feature(session, person['face'], FeatureType.get(name='face'))

        for eye in person['eye']:
            create_feature(session, eye, FeatureType.get(name='eye'), parent=parent)

        # make feature eyes
        eyes = person['eye'][:2]
        if len(eyes) == 2:
            x1, y1, width1, height1 = map(int, eyes[0])
            x2, y2, width2, height2 = map(int, eyes[1])

            eyes_params = (
                min(x1, x2),
                min(y1, y2),
                max(x1 + width1, x2 + width2) - min(x1, x2),
                max(y1 + height1, y2 + height2) - min(y1, y2),
            )

            create_feature(session, eyes_params, FeatureType.get(name='eyes'), parent=parent)

        for nose in person['nose']:
            create_feature(session, nose, FeatureType.get(name='nose'), parent=parent)

        for mouth in person['mouth']:
            create_feature(session, mouth, FeatureType.get(name='mouth'), parent=parent)


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


# sessions

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
def close_session(session_id):
    session = Session[session_id]
    session.status = STATUS_CLOSE


@db_session
def get_file_origin(photo_id):
    return Photo[photo_id].file_origin


@db_session
def get_current_photo_id(user_id):
    session_id = get_current_session_id(user_id)

    if Session[session_id].photo:
        return Session[session_id].photo.id


@db_session
def get_session_name(session_id):
    return Session[session_id].name


@db_session
def get_current_session_id(user_id):
    return Session.get(status=STATUS_CURRENT, user=User[user_id]).id


@db_session
def get_session_by_name(name):
    return Session.get(name=name).id


@db_session
def get_session_list(user_id):
    return list(select(s for s in Session if s.user == User[user_id]))
