from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Contributor, Issue, Project, Comment
from django.contrib.auth.models import User


class ContributorAPI(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='user1', email='user1@a.com', password='pass1'
        )
        self.user_2 = User.objects.create_user(
            username='user2', email='user2@a.com', password='pass2'
        )
        self.user_3 = User.objects.create_user(
            username='user3', email='user3@a.com', password='pass3'
        )
        self.contributor_1 = Contributor.objects.create(
            user=self.user_1, can_be_contacted=True, can_data_be_shared=True
        )
        self.contributor_2 = Contributor.objects.create(
            user=self.user_2, can_be_contacted=False, can_data_be_shared=False
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.contributor_1).access_token}'
        )

    def test_contributor_get_list(self):
        response: Response = self.client.get('/api/Contributor/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("count"), 2)

    def test_contributor_get_obj(self):
        response: Response = self.client.get(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), self.contributor_2.id)

    def test_contributor_post_minimal_data(self):
        data = {"username": "new_user", "password": "mypass", "age": 15}
        response: Response = self.client.post('/api/Contributor/', data=data)
        self.assertEqual(response.status_code, 201)
        new_contributor = Contributor.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_contributor.username, "new_user")
        self.assertNotEqual(new_contributor.user.password, "mypass")
        self.assertEqual(new_contributor.age, 15)
        self.assertEqual(new_contributor.can_be_contacted, False)
        self.assertEqual(new_contributor.can_data_be_shared, False)

    def test_contributor_post_fulll_data(self):
        data = {"username": "new_user", "password": "mypass", "age": 15,
                "can_be_contacted": True, "can_data_be_shared": True}
        response: Response = self.client.post('/api/Contributor/', data=data)
        self.assertEqual(response.status_code, 201)
        new_contributor = Contributor.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_contributor.username, "new_user")
        self.assertNotEqual(new_contributor.user.password, "mypass")
        self.assertEqual(new_contributor.age, 15)
        self.assertEqual(new_contributor.can_be_contacted, True)
        self.assertEqual(new_contributor.can_data_be_shared, True)

    def test_contributor_post_username_exist(self):
        data = {"username": "new_user", "password": "mypass", "age": 15}
        response: Response = self.client.post('/api/Contributor/', data=data)
        self.assertEqual(response.status_code, 201)
        new_contributor = Contributor.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_contributor.username, "new_user")
        response: Response = self.client.post('/api/Contributor/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_contributor_post_age_under_16(self):
        data = {"username": "new_user", "password": "mypass", "age": 14}
        response: Response = self.client.post('/api/Contributor/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_contributor_put_obj(self):
        data = {"username": "new_username", "password": "new_pass", "age": 65,
                "can_be_contacted": False, "can_data_be_shared": False}
        response: Response = self.client.put(
            f'/api/Contributor/{self.contributor_1.id}/', data=data
        )
        self.assertEqual(response.status_code, 200)
        contributor = Contributor.objects.filter(pk=self.contributor_1.id).first()
        self.assertEqual(contributor.username, "new_username")
        self.assertNotEqual(contributor.user.password, "new_pass")
        self.assertEqual(contributor.age, 65)
        self.assertEqual(contributor.can_be_contacted, False)
        self.assertEqual(contributor.can_data_be_shared, False)

    def test_contributor_patch_obj(self):
        data = {"age": 65}
        response: Response = self.client.patch(
            f'/api/Contributor/{self.contributor_1.id}/', data=data
        )
        self.assertEqual(response.status_code, 200)
        contributor = Contributor.objects.filter(pk=self.contributor_1.id).first()
        self.assertEqual(contributor.username, "user1")
        self.assertNotEqual(contributor.user.password, "mypass")
        self.assertEqual(contributor.age, 65)
        self.assertEqual(contributor.can_be_contacted, True)
        self.assertEqual(contributor.can_data_be_shared, True)

    def test_contributor_delete_obj(self):
        response: Response = self.client.delete(f'/api/Contributor/{self.contributor_1.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(Contributor.objects.filter(pk=self.contributor_1.id).first())
        self.assertIsNone(User.objects.filter(pk=self.contributor_1.user.id).first())

    def test_contributor_not_permitted(self):
        response: Response = self.client.patch(f'/api/Contributor/{self.contributor_2.id}/', {})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.put(f'/api/Contributor/{self.contributor_2.id}/', {})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.delete(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 403)

    def test_contributor_obj_not_found(self):
        response: Response = self.client.get('/api/Contributor/1111111111/')
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.put('/api/Contributor/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.patch('/api/Contributor/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.delete('/api/Contributor/1111111111/', data={})
        self.assertEqual(response.status_code, 404)

    def test_contributor_authenticated_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer invalidtoken')
        response: Response = self.client.get('/api/Contributor/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.post('/api/Contributor/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.get(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.put(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.patch(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.delete(f'/api/Contributor/{self.contributor_2.id}/')
        self.assertEqual(response.status_code, 401)
