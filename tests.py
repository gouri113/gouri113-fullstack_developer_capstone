import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import CarMake, CarModel
from .populate import initiate


class DjangoAppModelTests(TestCase):
    def setUp(self):
        self.make = CarMake.objects.create(name="Honda", description="The Power of Dreams")
        self.model = CarModel.objects.create(
            car_make=self.make,
            name="Civic",
            type="SEDAN",
            year=2022
        )

    def test_car_make_str(self):
        self.assertEqual(str(self.make), "Honda")

    def test_car_model_str(self):
        self.assertEqual(str(self.model), "Honda Civic")

    def test_populate_idempotency(self):
        initiate()
        count1 = CarModel.objects.count()
        initiate()
        count2 = CarModel.objects.count()
        self.assertEqual(count1, count2)


class DjangoAppAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.reg_url = '/djangoapp/register'
        self.login_url = '/djangoapp/login'
        self.logout_url = '/djangoapp/logout'

    def test_user_registration_and_login_flow(self):
        # Register new user
        reg_payload = {
            "userName": "unit_test_user",
            "firstName": "Unit",
            "lastName": "Tester",
            "email": "unittester@example.com",
            "password": "SecurePassword123!"
        }
        res = self.client.post(self.reg_url, data=json.dumps(reg_payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("status"), "Authenticated")

        # Duplicate registration
        dup_res = self.client.post(self.reg_url, data=json.dumps(reg_payload), content_type="application/json")
        self.assertEqual(dup_res.status_code, 200)
        self.assertEqual(dup_res.json().get("error"), "Already Registered")

        # Logout
        logout_res = self.client.get(self.logout_url)
        self.assertEqual(logout_res.status_code, 200)
        self.assertEqual(logout_res.json().get("userName"), "")

        # Login with correct credentials
        login_payload = {
            "userName": "unit_test_user",
            "password": "SecurePassword123!"
        }
        login_res = self.client.post(self.login_url, data=json.dumps(login_payload), content_type="application/json")
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.json().get("status"), "Authenticated")

        # Login with incorrect password
        bad_payload = {
            "userName": "unit_test_user",
            "password": "WrongPassword!"
        }
        bad_res = self.client.post(self.login_url, data=json.dumps(bad_payload), content_type="application/json")
        self.assertIsNone(bad_res.json().get("status"))


class DjangoAppViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_cars_endpoint(self):
        res = self.client.get('/djangoapp/get_cars')
        self.assertEqual(res.status_code, 200)
        self.assertIn("CarModels", res.json())
        self.assertGreater(len(res.json()["CarModels"]), 0)

    def test_static_pages_render(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/about').status_code, 200)
        self.assertEqual(self.client.get('/contact').status_code, 200)

    def test_add_review_anonymous_forbidden(self):
        payload = {
            "name": "Anon",
            "dealership": 1,
            "review": "Nice car",
            "purchase": True
        }
        res = self.client.post('/djangoapp/add_review', data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("status"), 403)

