import os
import sys
import mock
import logging

from django.conf import settings
from django.test import TestCase
from webapp import steps
from webapp.models import NetworkInstall

from webapp.tests.factories import ActivityFactory, UserFactory
from webapp.tests.factories import OrderFactory, NetworkFactory, ServerFactory

sys.path.append(os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '../../../../', 'src/py')))


def mock_retry(*dargs, **dkw):
    """
    Disable retrying decorator
    (it's a mock for the decorator)
    """
    if len(dargs) == 1 and callable(dargs[0]):
        return dargs[0]
    else:
        def wrap(f):
            def wrapped_f(*args, **kw):
                return f(*args, **kw)
            return wrapped_f
        return wrap

mock.patch('retrying.retry', mock_retry).start()


from webapp.tasks import create_server_foreman


class TasksTestCase(TestCase):

    def setUp(self):
        order = OrderFactory(order_id=0)
        ActivityFactory(activity_code_id=1)
        server = ServerFactory(order=order, username='admin', servername='testsrv')
        self.network = NetworkFactory(server=server, vlan_info=[{'ip':'127.0.0.1'}])
        self.logger = logging.getLogger()
        settings.LOCAL_VERSION = False



    @mock.patch('webapp.steps.ip_address_reservation.subprocess.Popen')
    def test_step0_ip_address_reservation(self, mock_subproc_popen):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'), 'returncode': 0}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        res = steps.ip_address_reservation.action(self.network, self.logger)

        self.assertTrue(mock_subproc_popen.called)
        self.assertEqual(res, {'data': '0 error output'})


    @mock.patch('webapp.steps.dns_record_creation.DnsAPI')
    def test_step1_dns_record_creation(self, mock_dns):
        mock_dns.create.return_value = 'data'

        res = steps.dns_record_creation.action(self.network, self.logger)

        self.assertEqual(res, {'data': 'data'})
        self.assertTrue(mock_dns.create.called)


    @mock.patch('webapp.steps.ip_address_reservation.subprocess')
    @mock.patch('webapp.steps.relocation_to_destination_vlan.subprocess')
    @mock.patch('webapp.steps.dns_record_creation.DnsAPI')
    @mock.patch('webapp.steps.os_installation.ForemanAPI')
    @mock.patch('webapp.steps.reboot_for_changes_to_take_effect.ForemanAPI')
    @mock.patch('webapp.steps.connectivity_check.sleep', return_value=None)
    @mock.patch('webapp.steps.tic_entry_creation.TicAPI')
    @mock.patch('webapp.steps.cts_entry_creation.CtsAPI')
    @mock.patch('webapp.steps.avamar_request_generation.AvamarAPI')
    @mock.patch('webapp.steps.final_checks_before_delivery.ForemanAPI')
    @mock.patch('webapp.steps.email_confirmation.sleep', return_value=None)
    def test_create_server_foreman(self, mock_sleep_confirmation,
                                   foreman_mock_final_checks,
                                   mock_avamar_api, mock_cts_api, mock_tic_api,
                                   mock_sleep_connectivity,
                                   foreman_mock_reboot, foreman_mock, mock_dns,
                                   mock_subprocess_relocation, mock_subprocess_reservation):

        # popen for ip_address_reservation
        process_mock_reservation = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'), 'returncode': 0}
        process_mock_reservation.configure_mock(**attrs)
        mock_subprocess_reservation.Popen.return_value = process_mock_reservation

        # popen for relocation_to_destination_vlan
        process_mock_relocation = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'), 'returncode': 0}
        process_mock_relocation.configure_mock(**attrs)
        mock_subprocess_relocation.Popen.return_value = process_mock_relocation

        # dns
        mock_dns.create.return_value = 'data'

        # foreman
        foreman_mock.show_status.return_value = {'status': 'Active'}

        foreman_mock_final_checks.index_hosts.return_value = {'results': [{'name':'testsrv.test.com','mac':'m1'}]}
        foreman_mock_final_checks.get_subnet_id.return_value = 1
        foreman_mock_final_checks.update_hosts.return_value = 'res'

        foreman_mock_reboot.do_power_action.return_value = {'power': 'message'}

        # TicAPI
        mock_tic_api.getHost.return_value = None
        mock_tic_api.getOs.return_value = 'rhel'
        mock_tic_api.getHw.return_value = 'hw'
        mock_tic_api.getDomain.return_value = 'domain'
        mock_tic_api.getAuthor.return_value = 'author'
        mock_tic_api.addHost.return_value = 1

        # CtsAPI
        mock_cts_api.getHost.return_value = None
        mock_cts_api.getOs.return_value = 'rhel'
        mock_cts_api.getDeviceType.return_value = 'dw'
        mock_cts_api.getActivityCode.return_value = 'ac'
        mock_cts_api.getHostingLevel.return_value = 'hl'
        mock_cts_api.getSupportLevel.return_value = 'sl'
        mock_cts_api.addHost.return_value = 1

        # AvamarAPI
        mock_avamar_api.getHost.return_value = None
        mock_avamar_api.addHost.return_value = 1


        self.user = UserFactory.create(username='admin', password='bar')

        result = create_server_foreman.delay(self.network, self.user)

        self.assertTrue(result.successful())

        self.assertTrue(mock_subprocess_relocation.Popen.called)
        self.assertTrue(mock_subprocess_reservation.Popen.called)

        # NetworkInstall.objects.get(network=self.network).data <- data here
