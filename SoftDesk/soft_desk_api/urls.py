from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContributorViewSet, ProjectViewSet, IssueViewSet, CommentViewSet, CustomTokenObtainPairView


router = DefaultRouter()
router.register(r'Contributor', ContributorViewSet)
router.register(r'Project', ProjectViewSet)
router.register(r'Issue', IssueViewSet)
router.register(r'Comment', CommentViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
