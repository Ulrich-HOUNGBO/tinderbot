from uuid import uuid4

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import Account


class AccountViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="uhoungbo@gmail.com", password="Password1!"
        )
        self.client.login(email="uhoungbo@gmail.com", password="Password1!")
        self.account = Account.objects.create(user=self.user, name="Test Account")

    def create_account_creates_new_account(self):
        data = {"name": "New Account", "user": self.user.id}
        response = self.client.post("/account/create_account/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 2)

    def get_all_account_returns_all_accounts_for_user(self):
        response = self.client.get("/account/get_all_account/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def get_account_returns_account_details(self):
        response = self.client.get(f"/account/get_account/{self.account.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Account")

    def get_account_returns_400_if_account_not_found(self):
        response = self.client.get(f"/account/get_account/{uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def update_account_updates_account_details(self):
        data = {"name": "Updated Account"}
        response = self.client.patch(
            f"/account/update_account/{self.account.id}/", data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, "Updated Account")

    def update_account_returns_400_if_account_not_found(self):
        data = {"name": "Updated Account"}
        response = self.client.patch(f"/account/update_account/{uuid4()}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def delete_account_deletes_account(self):
        response = self.client.delete(f"/account/delete_account/{self.account.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Account.objects.count(), 0)

    def delete_account_returns_400_if_account_not_found(self):
        response = self.client.delete(f"/account/delete_account/{uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
