# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import threading

from celery.app import shared_task
from celery.utils.log import get_task_logger
from .utils import celery_enabled, test_running
from .helpers import gs_slurp

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def geoserver_update_layers(self, *args, **kwargs):
    """
    Runs update layers.
    """
    return gs_slurp(*args, **kwargs)


@shared_task(bind=True)
def thumbnail_task(self, instance, overwrite=False, check_bbox=False):
    from .helpers import create_gs_thumbnail
    create_gs_thumbnail(instance, overwrite, check_bbox)


def async_thumbnail(instance, overwrite=False, check_bbox=False):
    if celery_enabled or test_running():
        thumbnail_task.delay(
            instance, overwrite=overwrite, check_bbox=check_bbox)
    else:
        t = threading.Thread(
            target=thumbnail_task.delay,
            args=(instance, ),
            kwargs={
                'overwrite': overwrite,
                'check_bbox': check_bbox
            })
        t.setDaemon(True)
        t.start()
