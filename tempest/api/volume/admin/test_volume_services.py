# Copyright 2014 NEC Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from tempest.api.volume import base
from tempest import config
from tempest.lib import decorators


CONF = config.CONF


def _get_host(host):
    return host.split('@')[0]


class VolumesServicesV2TestJSON(base.BaseVolumeAdminTest):
    """Tests Volume Services API.

    volume service list requires admin privileges.
    """

    @classmethod
    def resource_setup(cls):
        super(VolumesServicesV2TestJSON, cls).resource_setup()
        cls.services = (cls.admin_volume_services_client.list_services()
                        ['services'])
        # NOTE: Cinder service-list API returns the list contains
        # "<host name>@<driver name>" like "nova-compute01@lvmdriver-1".
        # So here picks <host name> up as a host.
        cls.host_name = _get_host(cls.services[0]['host'])
        cls.binary_name = cls.services[0]['binary']

    @decorators.idempotent_id('e0218299-0a59-4f43-8b2b-f1c035b3d26d')
    def test_list_services(self):
        services = (self.admin_volume_services_client.list_services()
                    ['services'])
        self.assertNotEqual(0, len(services))

    @decorators.idempotent_id('63a3e1ca-37ee-4983-826d-83276a370d25')
    def test_get_service_by_service_binary_name(self):
        services = (self.admin_volume_services_client.list_services(
            binary=self.binary_name)['services'])
        self.assertNotEqual(0, len(services))
        for service in services:
            self.assertEqual(self.binary_name, service['binary'])

    @decorators.idempotent_id('178710e4-7596-4e08-9333-745cb8bc4f8d')
    def test_get_service_by_host_name(self):
        services_on_host = [service for service in self.services if
                            _get_host(service['host']) == self.host_name]

        services = (self.admin_volume_services_client.list_services(
            host=self.host_name)['services'])

        # we could have a periodic job checkin between the 2 service
        # lookups, so only compare binary lists.
        s1 = map(lambda x: x['binary'], services)
        s2 = map(lambda x: x['binary'], services_on_host)
        # sort the lists before comparing, to take out dependency
        # on order.
        self.assertEqual(sorted(s1), sorted(s2))

    @decorators.idempotent_id('ffa6167c-4497-4944-a464-226bbdb53908')
    def test_get_service_by_service_and_host_name(self):

        services = (self.admin_volume_services_client.list_services(
            host=self.host_name, binary=self.binary_name))['services']

        self.assertNotEqual(0, len(services))
        self.assertEqual(self.host_name, _get_host(services[0]['host']))
        self.assertEqual(self.binary_name, services[0]['binary'])


class VolumesServicesV1TestJSON(VolumesServicesV2TestJSON):
    _api_version = 1
