#!/bin/sh -x

if [ ! -d .ve ]; then
    virtualenv .ve
    .ve/bin/python setup.py develop
    .ve/bin/easy_install south
fi

.ve/bin/django-admin.py $* --settings=redisboard_sample_project.settings


