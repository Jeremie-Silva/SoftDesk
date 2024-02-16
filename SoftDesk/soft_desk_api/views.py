from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from .permissions import IsContributorOrOwner, IsOwnerOrReadOnly
from .models import Contributor, Project, Issue, Comment
from .serializers import ContributorSerializer, ProjectSerializer, \
    IssueSerializer, CommentSerializer


class ContributorViewSet(ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action == "list":
            return Contributor.objects.all()
        else:
            return Contributor.objects.filter(id=self.kwargs.get("pk"))

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.request.user)
        return Response(status=HTTP_200_OK)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.none()  # redefined in get_queryset()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]

    def get_queryset(self):
        if self.action == "list":
            return self.request.user.contributor.projects_contribution.all()
        else:
            return Project.objects.filter(id=self.kwargs.get("pk"))

    def perform_create(self, serializer):
        contributors: list[Contributor] = [self.request.user.contributor]
        if self.request.data.get("contributors"):
            for name in self.request.data.get("contributors").split(","):
                contributor = Contributor.objects.filter(user__username=name.strip()).first()
                contributors.append(contributor)
        serializer.save(
            author=self.request.user.contributor,
            contributors=contributors
        )


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.none()  # redefined in get_queryset()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]

    def get_queryset(self):
        if self.action == "list":
            assigned_issues: Issue = self.request.user.contributor.assigned_issues.all()
            authored_issues: Issue = self.request.user.contributor.authored_issues.all()
            issues: QuerySet = assigned_issues | authored_issues
            return issues.distinct()
        else:
            return Issue.objects.filter(id=self.kwargs.get("pk"))


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.none()  # redefined in get_queryset()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]

    def get_queryset(self):
        if self.action == "list":
            user_contributor = self.request.user.contributor
            project_ids = user_contributor.projects_contribution.values_list('id', flat=True)
            project_comments = Comment.objects.filter(issue__project__id__in=project_ids).distinct()
            return project_comments
        else:
            return Comment.objects.filter(id=self.kwargs.get("pk"))


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response: dict = super().post(request, *args, **kwargs).data
        response.pop("refresh", None)
        return Response(response)
