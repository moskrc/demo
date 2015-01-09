# -*- coding: utf-8
import uuid

def make_uniq_key():
    uid = uuid.uuid4()
    return uid.hex