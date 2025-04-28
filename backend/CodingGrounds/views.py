from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

import requests
import time
import json
import random

# Create your views here.
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import GameSession, Badge, CodingProfile, CodingProblem, Submission, GameParticipation

from .serializers import (
    BadgeSerializer,
    CodingProfileSerializer,
    CodingProblemSerializer,
    SubmissionSerializer,
    GameSessionSerializer,
    GameParticipationSerializer,
    UserLoginSerializer
)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from .websocket_utils import WebSocketManager

def mainView(request):
    return render(request,"coding-grounds-app.html")

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'display_name': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: openapi.Response('User created successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'profile': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'display_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'streak': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_solved': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    )
                }
            )),
            400: 'Bad Request',
        }
    )
    def post(self, request):
        serializer = CodingProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            token, _ = Token.objects.get_or_create(user=profile.user)
            return Response({
                'token': token.key,
                'profile': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            200: openapi.Response('Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'profile': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'display_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'streak': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_solved': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    )
                }
            )),
            401: 'Unauthorized',
            404: 'Profile not found',
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        token, _ = Token.objects.get_or_create(user=user)
        
        try:
            profile = user.coding_profile
            return Response({
                'token': token.key,
                'profile': CodingProfileSerializer(profile).data
            })
        except CodingProfile.DoesNotExist:
            return Response({
                'token': token.key,
                'error': 'No coding profile found for this user'
            }, status=status.HTTP_404_NOT_FOUND)

class BadgeView(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    queryset = Badge.objects.all()
    permission_classes = [IsAuthenticated]

class CodingProfileView(viewsets.ModelViewSet):
    serializer_class = CodingProfileSerializer
    queryset = CodingProfile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return CodingProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

class CodingProblemView(viewsets.ModelViewSet):
    serializer_class = CodingProblemSerializer
    queryset = CodingProblem.objects.all()
    permission_classes = [IsAuthenticated]

class SubmissionView(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only show submissions for the current user"""
        return self.queryset.filter(profile=self.request.user.coding_profile)

    def list(self, request, *args, **kwargs):
        """List all submissions for the current user"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get details of a specific submission"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a submission"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class GameSessionView(viewsets.ModelViewSet):
    serializer_class = GameSessionSerializer
    queryset = GameSession.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.coding_profile
        # Show sessions where user is either creator or participant
        return GameSession.objects.filter(
            models.Q(created_by=profile) | 
            models.Q(participants=profile)
        ).distinct()

    def get_leaderboard_data(self, session):
        """Helper method to get leaderboard data"""
        participants_data = []
        for participation in GameParticipation.objects.filter(game_session=session).order_by('-problems_solved', 'total_time'):
            minutes, seconds = divmod(participation.total_time, 60)
            formatted_time = f"{minutes:02d}:{seconds:02d}"
            
            participant_data = {
                'profile_id': participation.profile.id,
                'username': participation.profile.display_name,
                'problems_solved': participation.problems_solved,
                'total_time': participation.total_time,
                'formatted_time': formatted_time,
                'score': participation.score
            }
            participants_data.append(participant_data)
        return participants_data
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create the session with the current user as creator
            session = GameSession.objects.create(
                created_by=request.user.coding_profile,
                **serializer.validated_data
            )
            
            # Add the creator as a participant
            session.participants.add(request.user.coding_profile)
            
            # Force save to ensure all changes are committed
            session.save()

            # Refresh the serializer with the saved instance
            serializer = self.get_serializer(session)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return Response(
                {"detail": f"Error creating session: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a game session"""
        try:
            # First check if session exists
            session = GameSession.objects.get(id=pk)
            profile = request.user.coding_profile
            
            # Check if session is full
            if session.max_participants > 0 and session.participants.count() >= session.max_participants:
                return Response(
                    {"detail": "Session is full"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if session is private and requires access code
            if session.is_private:
                access_code = request.data.get('access_code')
                if not access_code:
                    return Response(
                        {"detail": "Access code is required for private sessions"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if access_code != session.access_code:
                    return Response(
                        {"detail": "Invalid access code"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                        
            # Check if already a participant
            if session.participants.filter(id=profile.id).exists():
                return Response(
                    {"detail": "Already a participant"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add as participant
            session.participants.add(profile)
            
            # Notify other participants
            WebSocketManager.notify_session_update(pk, 'join', {
                'type': 'participant_joined',
                'profile': CodingProfileSerializer(profile).data
            })
            
            return Response(
                {"detail": "Successfully joined session"}, 
                status=status.HTTP_200_OK
            )
            
        except GameSession.DoesNotExist:
            return Response(
                {"detail": "Session not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error joining session: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a game session"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        if not session.participants.filter(id=profile.id).exists():
            return Response(
                {"detail": "Not a participant"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.participants.remove(profile)
        WebSocketManager.notify_session_update(pk, 'leave', {
            'type': 'participant_left',
            'profile': CodingProfileSerializer(profile).data
        })
        
        return Response(
            {"detail": "Successfully left session"}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def ready(self, request, pk=None):
        """Mark yourself as ready to start"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        if not session.participants.filter(id=profile.id).exists():
            return Response(
                {"detail": "Not a participant"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participation = GameParticipation.objects.get(
            game_session=session,
            profile=profile
        )
        participation.is_ready = True
        participation.save()
        
        # Check if all participants are ready
        all_ready = session.all_participants_ready()

        WebSocketManager.notify_session_update(pk, 'ready', {
            'type': 'participant_ready',
            'profile': CodingProfileSerializer(profile).data,
            'all_ready': all_ready
        })
        
        return Response(
            {"detail": "Ready status updated"}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the game session (only creator can do this)"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        if session.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only creator can start session"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if all participants are ready
        if not session.all_participants_ready():
            return Response({"detail": "Not all participants are ready"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if not session.participants.count() >= 2:
            return Response(
                {"detail": "Need at least 2 participants"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Select a random problem
        problems = CodingProblem.objects.all()
        if not problems.exists():
            return Response(
                {"detail": "No problems available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        random_problem = random.choice(problems)
        session.problems.clear()
        session.problems.add(random_problem)
        
        session.is_active = True
        session.start_time = timezone.now()
        session.save()
        
        WebSocketManager.notify_session_update(pk, 'start', {
            'type': 'session_started',
            'start_time': session.start_time.isoformat(),
            'problem': CodingProblemSerializer(random_problem).data
        })
        
        return Response({
            "detail": "Session started",
            "problem": CodingProblemSerializer(random_problem).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True)
    def problems(self, request, pk=None):
        """Get problems for this session"""
        session = self.get_object()
        # print(request.data)
        profile = request.user.coding_profile
        
        # Check if user is participant
        if not session.participants.filter(id=profile.id).exists():
            return Response({"detail": "Not a participant in this session"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Only show problems if session has started
        if not session.start_time or session.start_time > timezone.now():
            return Response({"detail": "Session hasn't started yet"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        problems = session.problems.all()
        serializer = CodingProblemSerializer(problems, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def leaderboard(self, request, pk=None):
        """Get leaderboard for this session"""
        session = self.get_object()
        leaderboard_data = self.get_leaderboard_data(session)
        return Response(leaderboard_data)

class GameParticipationView(viewsets.ModelViewSet):
    serializer_class = GameParticipationSerializer
    queryset = GameParticipation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(profile=self.request.user.coding_profile)

class SolveProblemView(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    lookup_field = "problem_id"
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']  # Allow GET and POST for Swagger visibility

    def coderunner(self, source_code, language, test_cases):
        # Dummy implementation for testing

        status_choices = [
            Submission.Status.PENDING,
            Submission.Status.ACCEPTED,
            Submission.Status.WRONG_ANSWER,
            Submission.Status.TIME_LIMIT_EXCEEDED,
            Submission.Status.MEMORY_LIMIT_EXCEEDED,
            Submission.Status.RUNTIME_ERROR,
            Submission.Status.COMPILATION_ERROR
        ]

        final_results = []
        for i, test_case in enumerate(test_cases):
            # Randomly select a status
            status = random.choice(status_choices)
            
            # Generate dummy output based on status
            if status == Submission.Status.ACCEPTED:
                output = json.dumps(test_case['expected_output'])
                error = None
            else:
                output = "No output"
                error = "Dummy error message" if status in [
                    Submission.Status.RUNTIME_ERROR,
                    Submission.Status.COMPILATION_ERROR
                ] else None

            final_results.append({
                "test_case": i + 1,
                "output": output,
                "expected": json.dumps(test_case['expected_output']),
                "match": status == Submission.Status.ACCEPTED,
                "error": error,
                "status": status,
                "time": f"{random.uniform(0.1, 2.0):.2f}s",
                "memory": f"{random.randint(100, 1000)}KB"
            })

        return final_results

    def list(self, request):
        """List all problems available for solving"""
        problems = CodingProblem.objects.all()
        serializer = CodingProblemSerializer(problems, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def details(self, request, problem_id=None):
        """Get details of a specific problem"""
        problem = get_object_or_404(CodingProblem, id=problem_id)
        serializer = CodingProblemSerializer(problem)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, problem_id=None):
        """Submit a solution for a problem"""
        problem = get_object_or_404(CodingProblem, id=problem_id)
        
        # Get session_id from request data
        session_id = request.data.get('session_id')
        if not session_id:
            return Response(
                {"detail": "Session ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        session = get_object_or_404(GameSession, id=session_id)
        profile = request.user.coding_profile
        
        # Check if user is a participant in the session
        if not session.participants.filter(id=profile.id).exists():
            return Response(
                {"detail": "Not a participant in this session"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if session is active
        if not session.is_active or (session.end_time and session.end_time < timezone.now()):
            return Response(
                {"detail": "Session is not active"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create submission
        submission = Submission.objects.create(
            profile=profile,
            problem=problem,
            code=request.data.get('code'),
            language=request.data.get('language', 'python'),
            game_session=session
        )
        
        # # Run the code
        # result = self.coderunner(
        #     submission.code, 
        #     submission.language, 
        #     problem.test_cases
        # )
        
        # Dummy result with all test cases passing
        result = [
            {'status': Submission.Status.ACCEPTED, 'output': 'Test case 1 passed'},
            {'status': Submission.Status.ACCEPTED, 'output': 'Test case 2 passed'},
            {'status': Submission.Status.ACCEPTED, 'output': 'Test case 3 passed'}
        ]

        # Update submission status based on result
        if all(r['status'] == Submission.Status.ACCEPTED for r in result):
            submission.status = Submission.Status.ACCEPTED
            
            # Get the participation record
            participation = GameParticipation.objects.get(
                game_session=session,
                profile=profile
            )
            
            # Check if this is the first time this user solved this problem in this session
            previous_accepted = Submission.objects.filter(
                profile=profile,
                problem=problem,
                game_session=session,
                status=Submission.Status.ACCEPTED
            ).exclude(pk=submission.pk).exists()
            
            if not previous_accepted:
                # Update participation statistics
                participation.problems_solved += 1
                
                # Calculate time since session start
                time_delta = submission.submitted_at - session.start_time
                seconds = int(time_delta.total_seconds())
                
                # Add to total time (used for tie-breaking)
                participation.total_time += seconds
                participation.save()
                
                # End the session since someone solved it
                session.end_time = timezone.now()
                session.is_active = False
                session.save()
                
                # Notify all participants of session end
                WebSocketManager.notify_session_update(
                    session_id,
                    'end',
                    {
                        'type': 'session_end',
                        'detail': "Session has ended - problem solved!",
                        'winner': profile.display_name,
                        'leaderboard': GameSessionView().get_leaderboard_data(session)
                    }
                )
        else:
            submission.status = Submission.Status.WRONG_ANSWER
        
        # Save the updated submission
        submission.save()
        
        # Update user profile
        profile.update_streak()
        
        return Response({
            'submission': SubmissionSerializer(submission).data,
            'result': result,
            'session_ended': submission.status == Submission.Status.ACCEPTED,
            'leaderboard': GameSessionView().get_leaderboard_data(session) if submission.status == Submission.Status.ACCEPTED else None
        }, status=status.HTTP_201_CREATED)

    # Override standard methods to return 405
    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed. Use /solve/{problem_id}/details/ to get problem details."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed. Use /solve/{problem_id}/submit/ to submit a solution."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        profile = request.user.coding_profile
        return Response(CodingProfileSerializer(profile).data)
    return Response(
        {"detail": "Not authenticated"}, 
        status=status.HTTP_401_UNAUTHORIZED
    )
