# Copyright (C) 2021 Fraunhofer Institut IOSB, Fraunhoferstr. 1, D 76131
# Karlsruhe, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
from requests.adapters import HTTPAdapter, Retry

from furl import furl
import logging

from frost_sta_client.config import Config

from frost_sta_client.dao import *
from frost_sta_client.service import auth_handler
from frost_sta_client.model.ext import entity_type


class SensorThingsService:
    def __init__(self, url, auth_handler=None, proxies=None):
        self.url = url
        self.auth_handler = auth_handler
        self.proxies = proxies
        config = Config()
        total_retries = config.total_retries
        connect =  config.connect
        backoff_factor = config.backoff_factor
        status_forcelist = config.status_forcelist
        self.request_session = requests.Session()

        retries = Retry(
            total=total_retries,
            connect=connect,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.request_session.mount("http://", adapter)
        self.request_session.mount("https://", adapter)

        if config.HTTP_AUTH:
            user = config.HTTP_AUTH_USER
            password = config.HTTP_AUTH_PASSWORD
            if user and password:
                self.request_session.auth = (user, password)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if value is None:
            self._url = value
            return
        try:
            self._url = furl(value)
        except ValueError as e:
            logging.error("received invalid url")
            raise e

    @property
    def auth_handler(self):
        return self._auth_handler

    @auth_handler.setter
    def auth_handler(self, value):
        if value is None:
            self._auth_handler = None
            return
        if not isinstance(value, auth_handler.AuthHandler):
            raise ValueError("auth should be of type AuthHandler!")
        self._auth_handler = value

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, value):
        if value is None:
            self._proxies = None
            return
        elif not isinstance(value, dict):
            raise ValueError("Proxies must be a Dictionary!")
        self._proxies = value

    def execute(self, method, url, **kwargs):
        if self.auth_handler is not None:
            #use normales requests if separate auth_handler is set
            response = self.request_session.request(
                method=method,
                url=url,
                proxies=self.proxies,
                auth=self.auth_handler.add_auth_header(),
                **kwargs,
            )
        else:
            response = self.request_session.request(
                method=method, url=url, proxies=self.proxies, **kwargs
            )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise e

        return response

    def get_path(self, parent, relation):
        if parent is None:
            return relation
        this_entity_type = entity_type.get_list_for_class(type(parent))
        _id = f"'{parent.id}'" if isinstance(parent.id, str) else parent.id
        return "{entity_type}({id})/{relation}".format(
            entity_type=this_entity_type, id=_id, relation=relation
        )

    def get_full_path(self, parent, relation):
        slash = "" if self.url.pathstr[-1] == "/" else "/"
        url = self.url.url + slash + self.get_path(parent, relation)
        return furl(url)

    def create(self, entity):
        entity.get_dao(self).create(entity)

    def update(self, entity):
        entity.get_dao(self).update(entity)

    def patch(self, entity, patches):
        entity.get_dao(self).patch(entity, patches)

    def delete(self, entity):
        entity.get_dao(self).delete(entity)

    def actuators(self):
        return actuator.ActuatorDao(self)

    def datastreams(self):
        return datastream.DatastreamDao(self)

    def features_of_interest(self):
        return features_of_interest.FeaturesOfInterestDao(self)

    def historical_locations(self):
        return historical_location.HistoricalLocationDao(self)

    def locations(self):
        return location.LocationDao(self)

    def multi_datastreams(self):
        return multi_datastream.MultiDatastreamDao(self)

    def observations(self):
        return observation.ObservationDao(self)

    def observed_properties(self):
        return observedproperty.ObservedPropertyDao(self)

    def sensors(self):
        return sensor.SensorDao(self)

    def tasks(self):
        return task.TaskDao(self)

    def tasking_capabilities(self):
        return tasking_capability.TaskingCapabilityDao(self)

    def things(self):
        return thing.ThingDao(self)
