import pathlib
import shutil
import tempfile

from django.test import TestCase, SimpleTestCase, Client, override_settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .views import *
from .models import *
from .forms import *

TEST_DIR = 'test_data'


# Create your tests here.


class TestUrls(SimpleTestCase):

    def test_items_url_resolve(self):
        url = reverse('item:items')
        self.assertEquals(resolve(url).func, items)

    def test_detail_url_resolve(self):
        url = reverse('item:detail', args=[1])
        self.assertEquals(resolve(url).func, detail)

    def test_new_url_resolve(self):
        url = reverse('item:new')
        self.assertEquals(resolve(url).func, new)

    def test_edit_url_resolve(self):
        url = reverse('item:edit', args=[1])
        self.assertEquals(resolve(url).func, edit)

    def test_delete_url_resolve(self):
        url = reverse('item:delete', args=[1])
        self.assertEquals(resolve(url).func, delete)


class TestViews(TestCase):
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='pharmacist1', password='Pharmacist123')
        self.client.login(username='pharmacist1', password='Pharmacist123')
        self.category = Category.objects.create(
            name='Medicine'
        )
        self.image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.item = Item.objects.create(
            category=self.category,
            name='Aspirin',
            description='It\'s asprin',
            price=2.20,
            image=SimpleUploadedFile(name='chair1.jpg', content=self.image, content_type='image/jpeg'),
            quantity=1000,
            is_with_prescription=False
        )

        # urls
        self.items_url = reverse('item:items')
        self.new_item_url = reverse('item:new')
        self.item_url = reverse('item:detail', args=[self.item.pk])
        self.edit_item_url = reverse('item:edit', args=[self.item.pk])
        self.delete_item_url = reverse('item:delete', args=[self.item.pk])

    def test_items_GET(self):
        response = self.client.get(self.items_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/items.html')

    def test_item_detail_GET(self):
        response = self.client.get(self.item_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')

    def test_item_detail_POST_buy_items(self):
        self.client.logout()
        old_quantity = self.item.quantity
        buying_quantity = 10
        expected_quantity = old_quantity - buying_quantity
        response = self.client.post(self.item_url, {
            'quantity': [f'{buying_quantity}']
        })
        self.item.refresh_from_db()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')
        self.assertEquals(self.item.quantity, expected_quantity)

    def test_item_detail_POST_buy_items_as_employee(self):
        expected_quantity = self.item.quantity
        buying_quantity = 10
        response = self.client.post(self.item_url, {
            'quantity': [f'{buying_quantity}']
        })
        self.item.refresh_from_db()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')
        self.assertEquals(self.item.quantity, expected_quantity)

    def test_item_detail_POST_negative_value(self):
        expected_quantity = self.item.quantity
        buying_quantity = -10
        response = self.client.post(self.item_url, {
            'quantity': [f'{buying_quantity}']
        })
        self.item.refresh_from_db()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')
        self.assertEquals(self.item.quantity, expected_quantity)

    def test_item_detail_POST_empty(self):
        self.client.logout()
        expected_quantity = self.item.quantity
        response = self.client.post(self.item_url)
        self.item.refresh_from_db()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/detail.html')
        self.assertEquals(self.item.quantity, expected_quantity)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_new_POST_create_new_item(self):
        response = self.client.post(self.new_item_url, {
            'category': [f'{self.category.pk}'],
            'name': ['Bepanten'],
            'description': ['It is good for hands'],
            'price': ['12'],
            'image': SimpleUploadedFile(name='chair1.jpg', content=self.image, content_type='image/jpeg'),
            'quantity': 10,
            'is_with_prescription': ['on']
        })

        self.assertRedirects(response, reverse('item:detail', args=[Item.objects.last().pk]))
        self.assertEquals(Item.objects.count(), 2)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_edit_item_POST(self):
        response = self.client.post(self.edit_item_url, {
            'category': [f'{self.category.pk}'],
            'name': ['Bepanten'],
            'description': ['It is good for hands'],
            'price': ['12'],
            'image': SimpleUploadedFile(name='chair1.jpg', content=self.image, content_type='image/jpeg'),
            'quantity': 10,
            'is_with_prescription': ['on']
        })
        self.item.refresh_from_db()

        self.assertRedirects(response, reverse('item:detail', args=[self.item.pk]))
        self.assertEquals(Item.objects.count(), 1)
        self.assertEquals(self.item.quantity, 10)
        self.assertEquals(self.item.name, 'Bepanten')

    def test_delete_item_DELETE(self):
        response = self.client.delete(self.delete_item_url)

        self.assertEquals(Item.objects.count(), 0)
        self.assertRedirects(response, reverse('dashboard:index'))


# TODO: test negative scenarios and client case scenarios. TestForm TestModel


def tearDownModule():
    print('\nDeleting temporary files...\n')
    try:
        shutil.rmtree(TEST_DIR)
    except OSError:
        pass
