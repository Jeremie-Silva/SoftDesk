from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import ContributorViewSet, ProjectViewSet, IssueViewSet, CommentViewSet, CustomTokenObtainPairView


router = DefaultRouter()
router.register(r'Contributor', ContributorViewSet)
router.register(r'Project', ProjectViewSet)
router.register(r'Issue', IssueViewSet)
router.register(r'Comment', CommentViewSet)


schema_view = get_schema_view(
    openapi.Info(
        title="Soft Desk API",
        default_version='v1',
        contact=openapi.Contact(email="silva.jeremie93@gmail.com"),
    ),
    public=True,
    permission_classes=[AllowAny,],
)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/ui/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-doc'),
]
