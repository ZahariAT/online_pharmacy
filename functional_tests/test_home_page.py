import shutil

from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import TestCase, SimpleTestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


from item.models import *

TEST_DIR = 'test_data'


class TestHomePage(StaticLiveServerTestCase):

    def setUp(self) -> None:
        # c_service = webdriver.ChromeService(executable_path='functional_tests/chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.browser = webdriver.Chrome(options=options)
        # self.browser = webdriver.Chrome(service=c_service)

    def tearDown(self) -> None:
        self.browser.close()

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_home_page(self):
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
        self.browser.get(self.live_server_url)
        import time
        time.sleep(1)

        # TODO: Maybe test different browsers just the main page. Think of whole scenarios and not small multiple ones


def tearDownModule():
    print('\nDeleting temporary files...\n')
    try:
        shutil.rmtree(TEST_DIR)
    except OSError as e:
        pass
