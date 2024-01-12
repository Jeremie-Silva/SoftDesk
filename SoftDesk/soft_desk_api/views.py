from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .permissions import IsContributorOrOwner
from .models import Contributor, Project, Issue, Comment
from .serializers import ContributorSerializer, ProjectSerializer, \
    IssueSerializer, CommentSerializer


class ContributorViewSet(ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]


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
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]

    def get_queryset(self):
        return Issue.objects.filter(project__contributors=self.request.user.contributor)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributorOrOwner]


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response: dict = super().post(request, *args, **kwargs).data
        response.pop("refresh", None)
        response["access"] = f"Bearer {response["access"]}"
        return Response(response)
