from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Contributor, Issue, Project, Comment
from django.contrib.auth.models import User


class ContributorAPI(APITestCase):
    def setUp(self):
        pass
