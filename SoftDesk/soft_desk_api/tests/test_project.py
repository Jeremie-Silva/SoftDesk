from drf_yasg.openapi import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, Token
from ..models import Contributor, Project
from django.contrib.auth.models import User


class ProjectPermissionsAPI(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='user1', email='user1@a.com', password='pass1'
        )
        self.user_2 = User.objects.create_user(
            username='user2', email='user2@a.com', password='pass2'
        )
        self.contributor_1 = Contributor.objects.create(
            user=self.user_1, can_be_contacted=True, can_data_be_shared=True
        )
        self.contributor_2 = Contributor.objects.create(
            user=self.user_2, can_be_contacted=True, can_data_be_shared=True
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.contributor_1).access_token}'
        )

        project_1 = Project.objects.create(
            id=99999, name="a", description="aaa", author=self.contributor_1
        )
        project_1.contributors.add(self.contributor_1)

        project_2 = Project.objects.create(
            id=88888, name="b", description="bbb", author=self.contributor_1
        )

        project_2.contributors.add(self.contributor_1)

        project_3 = Project.objects.create(
            id=77777, name="c", description="ccc", author=self.contributor_2
        )
        project_3.contributors.add(self.contributor_2)

        project_4 = Project.objects.create(
            id=66666, name="d", description="ddd", author=self.contributor_2
        )
        project_4.contributors.add(self.contributor_1)
        project_4.contributors.add(self.contributor_2)

    def test_projects_get_list(self):
        response: Response = self.client.get('/api/Project/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("count"), 3)

    def test_project_get_obj(self):
        response: Response = self.client.get('/api/Project/99999/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), 99999)

    def test_project_post(self):
        data = {"name": "e", "description": "eee", "type": "BE"}
        response: Response = self.client.post('/api/Project/', data=data)
        self.assertEqual(response.status_code, 201)
        new_project = Project.objects.filter(name="e").first()
        response: Response = self.client.get(f'/api/Project/{new_project.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_project.author, self.contributor_1)
        self.assertIn(self.contributor_1, new_project.contributors.all())

    def test_project_post_multiple_contributors(self):
        data = {"name": "e", "description": "eee", "type": "BE", "contributors": "user2"}
        response: Response = self.client.post('/api/Project/', data=data)
        self.assertEqual(response.status_code, 201)
        new_project = Project.objects.filter(name="e").first()
        self.assertEqual(new_project.author, self.contributor_1)
        self.assertIn(self.contributor_1, new_project.contributors.all())
        self.assertIn(self.contributor_2, new_project.contributors.all())

    def test_project_put_obj(self):
        data = {"name": "new_name", "description": "aaa", "author": self.contributor_1}
        response: Response = self.client.put('/api/Project/99999/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("name"), "new_name")

    def test_project_patch_obj(self):
        data = {"name": "new_name"}
        response: Response = self.client.patch('/api/Project/99999/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("name"), "new_name")

    def test_project_delete_obj(self):
        response: Response = self.client.delete('/api/Project/99999/')
        self.assertEqual(response.status_code, 204)
        response: Response = self.client.get('/api/Project/99999/')
        self.assertEqual(response.status_code, 404)

    def test_project_obj_not_permitted(self):
        response: Response = self.client.get('/api/Project/77777/')
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.put('/api/Project/77777/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.patch('/api/Project/77777/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.delete('/api/Project/77777/', data={})
        self.assertEqual(response.status_code, 403)

    def test_project_obj_not_found(self):
        response: Response = self.client.get('/api/Project/1111111111/')
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.put('/api/Project/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.patch('/api/Project/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.delete('/api/Project/1111111111/', data={})
        self.assertEqual(response.status_code, 404)

    def test_project_authenticated_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer faketoken')
        response: Response = self.client.get('/api/Project/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.post('/api/Project/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.get('/api/Project/99999/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.put('/api/Project/99999/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.patch('/api/Project/99999/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.delete('/api/Project/99999/')
        self.assertEqual(response.status_code, 401)
