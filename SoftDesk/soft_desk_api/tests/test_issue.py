from drf_yasg.openapi import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Contributor, Issue, Project
from django.contrib.auth.models import User


class IssuePermissionsAPI(APITestCase):
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
            id=44444, project=project_1, author=self.contributor_2,
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

    def test_issue_post(self):
        data = {"project": 99999, "assigned_contributor": "eee", "type": "BE"}
        response: Response = self.client.post('/api/Project/', data=data)
        self.assertEqual(response.status_code, 201)
        new_project = Project.objects.filter(name="e").first()
        response: Response = self.client.get(f'/api/Project/{new_project.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_project.author, self.contributor_1)
        self.assertIn(self.contributor_1, new_project.contributors.all())


"""
    projet_1 : 2 contribs
    projet_2 : 1 contrib
    issue_1 : LOW BUG TO DO
    issue_2 : MEDIUM FEATURE In Progress
    issue_3 : HIGH TASK Finished

    default_state
    default_conrib



    contrib_1 -> get 404
    contrib_1 -> get 401

    post_with_another_contrib

    post_forbidenn_contrib
    
"""
