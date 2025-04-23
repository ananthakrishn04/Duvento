"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from CodingGrounds.views import (
    BadgeView,
    CodingProblemView,
    CodingProfileView,
    SubmissionView,
    GameParticipationView,
    GameSessionView,
    SolveProblemView,
    UserLoginView,
    UserRegistrationView,
    current_user,
)

from CodingGrounds.swagger import schema_view

router = routers.DefaultRouter()
router.register(r'badges', BadgeView, basename='badge')
router.register(r'profiles', CodingProfileView, basename='profile')
router.register(r'problems', CodingProblemView, basename='problem')
router.register(r'submissions', SubmissionView, basename='submission')
router.register(r'sessions', GameSessionView, basename='session')
router.register(r'participations', GameParticipationView, basename='participation')
router.register(r'solve', SolveProblemView, basename='solve')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/auth/login/', UserLoginView.as_view(), name='user-login'),
    path('api/auth/me/', current_user, name='current-user'),
]
