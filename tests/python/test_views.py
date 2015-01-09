from django.core.urlresolvers import reverse
from django.test import TestCase
from webapp.tests.factories import UserFactory, ServerFactory, NetworkInstallFactory, NetworkFactory, OrderFactory, \
    ActivityFactory


class MyServersAuthTestCase(TestCase):
    def setUp(self):
        OrderFactory(order_id=0)
        ActivityFactory(activity_code_id=1)


    def test_deny(self):
        response = self.client.get(reverse("webapp_my_servers"))
        self.assertEqual(response.status_code, 302)

    def test_allow(self):
        UserFactory.create(username='foo', password='bar')
        self.assertTrue(self.client.login(username='foo', password='bar'))

        response = self.client.get(reverse("webapp_my_servers"))
        self.assertEqual(response.status_code, 200)


class MyServersTestCase(TestCase):
    def setUp(self):
        OrderFactory(order_id=0)
        ActivityFactory(activity_code_id=1)
        UserFactory.create(username='foo', password='bar')
        self.client.login(username='foo', password='bar')


    def test_header(self):
        response = self.client.get(reverse("webapp_my_servers"))
        self.assertIn('My server requests', response.content)

    def test_list(self):
        order = OrderFactory(order_id=1)
        server = ServerFactory(order=order, servername='My Test Server', username='foo')
        network = NetworkFactory(server=server)
        NetworkInstallFactory(network=network)

        response = self.client.get(reverse("webapp_my_servers"))

        self.assertIn('My server requests', response.content)


class NewServerRequestTestCase(TestCase):
    def setUp(self):
        OrderFactory(order_id=0)
        ActivityFactory(activity_code_id=1)
        UserFactory.create(username='foo', password='bar')
        self.client.login(username='foo', password='bar')

    def test_quantity_fail(self):
        order = OrderFactory(order_id=1, check_quantity=1, quantity=1)
        ServerFactory(order=order)

        # try to add a second server (limit is 1 serer only)
        resp = self.client.post(reverse('new_server', kwargs={}), {
            'add_server_wizard-current_step': 'server',
            'server-order': 1,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form']['order'].errors, [u'Limit is reached'])

    def test_quantity_success(self):
        order = OrderFactory(order_id=1, check_quantity=1, quantity=99)

        # lets create a ten of servers
        for r in range(10):
            ServerFactory(order=order)

        # try to add another server
        resp = self.client.post(reverse('new_server', kwargs={}), {
            'add_server_wizard-current_step': 'server',
            'server-order': 1,
        })

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['form']['order'].errors, [])

    def test_quantity_unlimited(self):
        order = OrderFactory(order_id=1, check_quantity=1, quantity=0)

        # lets create a ten of servers
        for r in range(10):
            ServerFactory(order=order)

        # try to add another server
        resp = self.client.post(reverse('new_server', kwargs={}), {
            'add_server_wizard-current_step': 'server',
            'server-order': 1,
        })

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['form']['order'].errors, [])

    def test_quantity_not_check(self):
        order = OrderFactory(order_id=1, check_quantity=0, quantity=1)

        # lets create a ten of servers
        for r in range(10):
            ServerFactory(order=order)

        # try to add another server
        resp = self.client.post(reverse('new_server', kwargs={}), {
            'add_server_wizard-current_step': 'server',
            'server-order': 1,
        })

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['form']['order'].errors, [])


class NewServerRequestCheckOrderCapacityTestCase(TestCase):
    def setUp(self):
        OrderFactory(order_id=0)
        ActivityFactory(activity_code_id=1)

    def test_response_with_check(self):
        order = OrderFactory(order_id=77, check_quantity=1, quantity=3)

        server1 = ServerFactory(order=order)

        resp = self.client.get(reverse('check_order_capacity', kwargs={}), {
            'order_id': order.pk,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '{"balance": 2}')

        # let's create another one..
        server2 = ServerFactory(order=order)

        resp = self.client.get(reverse('check_order_capacity', kwargs={}), {
            'order_id': order.pk,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '{"balance": 1}')

    def test_response_with_unlim(self):
        order1 = OrderFactory(order_id=77, check_quantity=0, quantity=0)

        server1 = ServerFactory(order=order1)

        resp = self.client.get(reverse('check_order_capacity', kwargs={}), {
            'order_id': order1.pk,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '{}')

        # and with check_quantity (it's the same)
        order2 = OrderFactory(order_id=78, check_quantity=1, quantity=0)

        server2 = ServerFactory(order=order2)

        resp = self.client.get(reverse('check_order_capacity', kwargs={}), {
            'order_id': order2.pk,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '{}')


