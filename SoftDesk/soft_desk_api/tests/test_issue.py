from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Contributor, Issue, Project
from django.contrib.auth.models import User


class IssueAPI(APITestCase):
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
        project_1.contributors.add(self.contributor_2)

        project_2 = Project.objects.create(
            id=88888, name="b", description="bbb", author=self.contributor_1
        )
        project_2.contributors.add(self.contributor_1)

        project_3 = Project.objects.create(
            id=33333, name="c", description="ccc", author=self.contributor_2
        )
        project_3.contributors.add(self.contributor_2)

        issue_1 = Issue.objects.create(
            id=77777, project=project_1, author=self.contributor_1,
            assigned_contributor=self.contributor_1, state="TO DO",
            priority="LOW", label="BUG"
        )

        issue_2 = Issue.objects.create(
            id=66666, project=project_1, author=self.contributor_1,
            assigned_contributor=self.contributor_2, state="In Progress",
            priority="MEDIUM", label="FEATURE"
        )

        issue_3 = Issue.objects.create(
            id=55555, project=project_1, author=self.contributor_2,
            assigned_contributor=self.contributor_1, state="In Progress",
            priority="MEDIUM", label="FEATURE"
        )

        issue_4 = Issue.objects.create(
            id=44444, project=project_3, author=self.contributor_2,
            assigned_contributor=self.contributor_2, state="Finished",
            priority="HIGH", label="TASK"
        )

    def test_issue_get_list(self):
        response: Response = self.client.get('/api/Issue/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("count"), 3)

    def test_issue_get_obj_from_author(self):
        response: Response = self.client.get('/api/Issue/66666/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), 66666)

    def test_issue_get_obj_from_contributor(self):
        response: Response = self.client.get('/api/Issue/55555/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), 55555)

    def test_issue_post_minimal_data(self):
        data = {"project": 99999}
        response: Response = self.client.post('/api/Issue/', data=data)
        self.assertEqual(response.status_code, 201)
        new_issue = Issue.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_issue.author, self.contributor_1)
        self.assertEqual(new_issue.assigned_contributor, self.contributor_1)
        self.assertEqual(new_issue.state, "TO DO")
        self.assertTrue(hasattr(new_issue, "created_time"))

    def test_issue_post_full_data(self):
        data = {
            "project": 99999, "assigned_contributor": "user1", "author": self.contributor_1,
            "state": "In Progress", "priority": "MEDIUM", "label": "FEATURE"
        }
        response: Response = self.client.post('/api/Issue/', data=data)
        self.assertEqual(response.status_code, 201)
        new_issue = Issue.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_issue.author, self.contributor_1)
        self.assertEqual(new_issue.assigned_contributor, self.contributor_1)
        self.assertEqual(new_issue.state, "In Progress")
        self.assertEqual(new_issue.priority, "MEDIUM")
        self.assertEqual(new_issue.label, "FEATURE")
        self.assertTrue(hasattr(new_issue, "created_time"))

    def test_issue_post_another_contributor_of_project(self):
        data = {
            "project": 99999, "assigned_contributor": "user2", "author": self.contributor_1,
            "state": "In Progress", "priority": "MEDIUM", "label": "FEATURE"
        }
        response: Response = self.client.post('/api/Issue/', data=data)
        self.assertEqual(response.status_code, 201)
        new_issue = Issue.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_issue.author, self.contributor_1)
        self.assertEqual(new_issue.assigned_contributor, self.contributor_2)

    def test_issue_post_not_author_or_contributor_of_project(self):
        data = {
            "project": 33333, "assigned_contributor": "user2", "author": self.contributor_1,
            "state": "In Progress", "priority": "MEDIUM", "label": "FEATURE"
        }
        response: Response = self.client.post('/api/Issue/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_issue_put_obj(self):
        data = {
            "project": 99999, "assigned_contributor": "user2", "author": self.contributor_1,
            "state": "In Progress", "priority": "MEDIUM", "label": "FEATURE"
        }
        response: Response = self.client.put('/api/Issue/77777/', data=data)
        self.assertEqual(response.status_code, 200)
        new_issue = Issue.objects.filter(pk=77777).first()
        self.assertEqual(new_issue.author, self.contributor_1)
        self.assertEqual(new_issue.assigned_contributor, self.contributor_2)
        self.assertEqual(new_issue.state, "In Progress")
        self.assertEqual(new_issue.priority, "MEDIUM")
        self.assertEqual(new_issue.label, "FEATURE")

    def test_issue_patch_obj(self):
        data = {"assigned_contributor": "user2"}
        response: Response = self.client.patch('/api/Issue/77777/', data=data)
        self.assertEqual(response.status_code, 200)
        new_issue = Issue.objects.filter(pk=77777).first()
        self.assertEqual(new_issue.assigned_contributor, self.contributor_2)

    def test_issue_delete_obj(self):
        response: Response = self.client.delete('/api/Issue/77777/')
        self.assertEqual(response.status_code, 204)
        response: Response = self.client.delete('/api/Issue/77777/')
        self.assertEqual(response.status_code, 404)

    def test_issue_obj_not_permitted(self):
        response: Response = self.client.get('/api/Issue/44444/')
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.put('/api/Issue/44444/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.patch('/api/Issue/44444/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.delete('/api/Issue/44444/', data={})
        self.assertEqual(response.status_code, 403)

    def test_issue_obj_not_found(self):
        response: Response = self.client.get('/api/Issue/1111111111/')
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.put('/api/Issue/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.patch('/api/Issue/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.delete('/api/Issue/1111111111/', data={})
        self.assertEqual(response.status_code, 404)

    def test_issue_authenticated_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer invalidtoken')
        response: Response = self.client.get('/api/Issue/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.post('/api/Issue/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.get('/api/Issue/66666/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.put('/api/Issue/66666/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.patch('/api/Issue/66666/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.delete('/api/Issue/66666/')
        self.assertEqual(response.status_code, 401)
