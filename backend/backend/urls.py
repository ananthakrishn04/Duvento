"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from rest_framework.authtoken.views import obtain_auth_token

from CodingGrounds.views import (
    BadgeView,
    CodingProblemView,
    CodingProfileView,
    SubmissionView,
    GameParticipationView,
    GameSessionView,
    # solve_problem_view
    SolveProblemView,
    UserLoginView,
    UserRegistrationView,
    current_user,
    code_editor_view,
    mainView
)

from rest_framework import routers


router = routers.DefaultRouter()

# router.register(r'Session',views.SessionView,'Session')
# router.register(r'solve/<int:id>/',solve_problem_view,basename="solve_problem")

# router.register(r'solve/<int:id>',SolveProblemView,basename="solve_problem")
router.register(r'badges', BadgeView, basename='badge')
router.register(r'profiles', CodingProfileView, basename='profile')
router.register(r'problems', CodingProblemView, basename='problem')
router.register(r'submissions', SubmissionView, basename='submission')
router.register(r'sessions', GameSessionView, basename='session')
router.register(r'participations', GameParticipationView, basename='participation')
# router.register(r'users',User)

urlpatterns = [
    path('', mainView),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("solve/<int:problem_id>/", SolveProblemView.as_view({"post": "create"}), name="solve-problem"),
    path("solve/<int:problem_id>/details/", SolveProblemView.as_view({"get": "problem_details"}), name="solve-problem-details"),
    path('auth/', include('rest_framework.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/users/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/users/login/', UserLoginView.as_view(), name='user-login'),
    path('api/users/me/', current_user, name='current-user'),
    path('api/editor',code_editor_view,name="editor")
]
