from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Contributor, Issue, Project, Comment
from django.contrib.auth.models import User


class CommentAPI(APITestCase):
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
            id=88888, name="b", description="bbb", author=self.contributor_2
        )
        project_2.contributors.add(self.contributor_2)

        issue_1 = Issue.objects.create(
            id=77777, project=project_1, author=self.contributor_2,
            assigned_contributor=self.contributor_1, state="TO DO",
            priority="LOW", label="BUG"
        )
        issue_2 = Issue.objects.create(
            id=66666, project=project_2, author=self.contributor_2,
            assigned_contributor=self.contributor_2, state="In Progress",
            priority="MEDIUM", label="FEATURE"
        )

        comment_1 = Comment.objects.create(
            id=11111, issue=issue_1, author=self.contributor_1, description="Some words"
        )
        comment_2 = Comment.objects.create(
            id=22222, issue=issue_1, author=self.contributor_2, description="Other words"
        )
        comment_3 = Comment.objects.create(
            id=33333, issue=issue_2, author=self.contributor_2, description="Some words"
        )

    def test_comment_get_list(self):
        response: Response = self.client.get('/api/Comment/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("count"), 2)

    def test_comment_get_obj_from_author(self):
        response: Response = self.client.get('/api/Comment/11111/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), 11111)

    def test_comment_get_obj_from_contributor(self):
        response: Response = self.client.get('/api/Comment/22222/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("id"), 22222)

    def test_comment_post(self):
        data = {"issue": 77777, "description": "Some words"}
        response: Response = self.client.post('/api/Comment/', data=data)
        self.assertEqual(response.status_code, 201)
        new_comment = Comment.objects.filter(pk=response.json().get("id")).first()
        self.assertEqual(new_comment.author, self.contributor_1)
        self.assertTrue(hasattr(new_comment, "created_time"))

    def test_comment_post_not_author_or_contributor_of_project(self):
        data = {"issue": 66666, "description": "Some words"}
        response: Response = self.client.post('/api/Comment/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_comment_put_obj(self):
        data = {"issue": 77777, "description": "Some new words"}
        response: Response = self.client.put('/api/Comment/11111/', data=data)
        self.assertEqual(response.status_code, 200)
        new_comment = Comment.objects.filter(pk=11111).first()
        self.assertEqual(new_comment.author, self.contributor_1)
        self.assertEqual(new_comment.description, "Some new words")

    def test_comment_patch_obj(self):
        data = {"description": "Some new words"}
        response: Response = self.client.patch('/api/Comment/11111/', data=data)
        self.assertEqual(response.status_code, 200)
        new_comment = Comment.objects.filter(pk=11111).first()
        self.assertEqual(new_comment.description, "Some new words")

    def test_comment_delete_obj(self):
        response: Response = self.client.delete('/api/Comment/11111/')
        self.assertEqual(response.status_code, 204)
        response: Response = self.client.delete('/api/Comment/11111/')
        self.assertEqual(response.status_code, 404)

    def test_comment_obj_not_permitted(self):
        response: Response = self.client.get('/api/Comment/33333/')
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.put('/api/Comment/33333/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.patch('/api/Comment/33333/', data={})
        self.assertEqual(response.status_code, 403)
        response: Response = self.client.delete('/api/Comment/33333/', data={})
        self.assertEqual(response.status_code, 403)

    def test_comment_obj_not_found(self):
        response: Response = self.client.get('/api/Comment/1111111111/')
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.put('/api/Comment/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.patch('/api/Comment/1111111111/', data={})
        self.assertEqual(response.status_code, 404)
        response: Response = self.client.delete('/api/Comment/1111111111/', data={})
        self.assertEqual(response.status_code, 404)

    def test_comment_authenticated_only(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer invalidtoken')
        response: Response = self.client.get('/api/Comment/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.post('/api/Comment/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.get('/api/Comment/11111/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.put('/api/Comment/11111/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.patch('/api/Comment/11111/')
        self.assertEqual(response.status_code, 401)
        response: Response = self.client.delete('/api/Comment/11111/')
        self.assertEqual(response.status_code, 401)
