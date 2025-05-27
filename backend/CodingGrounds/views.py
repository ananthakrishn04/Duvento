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

    @action(detail=False, methods=['get'])
    def game_history(self, request):
        """Get the game history for the current user"""
        profile = request.user.coding_profile
        
        # Get all game participations for this user
        participations = GameParticipation.objects.filter(
            profile=profile
        ).select_related('game_session').order_by('-game_session__end_time')
        
        # Format the history data
        history_data = []
        
        for participation in participations:
            session = participation.game_session
            
            # Skip sessions that haven't ended
            if not session.end_time:
                continue
                
            # Find opponent in 1v1 games
            opponent = None
            if session.participants.count() == 2:
                opponent = session.participants.exclude(id=profile.id).first()
            
            # Determine if user won (in 1v1 games)
            result = "UNKNOWN"
            if session.participants.count() == 2:
                # Get the other participant's game participation
                opponent_participation = GameParticipation.objects.filter(
                    game_session=session,
                    profile=opponent
                ).first() if opponent else None
                
                if opponent_participation:
                    if participation.problems_solved > opponent_participation.problems_solved:
                        result = "WIN"
                    elif participation.problems_solved < opponent_participation.problems_solved:
                        result = "LOSE"
                    else:
                        # If same number of problems solved, compare time
                        if participation.total_time < opponent_participation.total_time:
                            result = "WIN"
                        else:
                            result = "LOSE"
            
            # Get problem info if available
            problem = session.problems.first()
            problem_info = {
                'id': problem.id,
                'title': problem.title
            } if problem else None
            
            # Format the data
            history_entry = {
                'session_id': str(session.id),
                'date': session.end_time.strftime('%b %d, %Y · %I:%M %p'),
                'problem': problem_info,
                'opponent': {
                    'id': opponent.id,
                    'display_name': opponent.display_name
                } if opponent else None,
                'result': result,
                'problems_solved': participation.problems_solved,
                'total_time': participation.total_time,
                'score': participation.score
            }
            
            history_data.append(history_entry)
        
        return Response(history_data)

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

    @action(detail=True, methods=['post'])
    def check_participants(self, request, pk=None):
        """Check if at least 2 people have joined the session"""
        try:
            session = self.get_object()
            participants_count = session.participants.count()
            
            return Response({
                "has_enough_participants": participants_count >= 2,
                "participants_count": participants_count,
                "required_count": 2
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Error checking participants: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def check_all_ready(self, request, pk=None):
        """Check if all participants in the session are ready"""
        try:
            session = self.get_object()
            all_ready = session.all_participants_ready()
            participants_count = session.participants.count()
            
            return Response({
                "all_ready": all_ready,
                "participants_count": participants_count,
                "ready_participants_count": session.participations.filter(is_ready=True).count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Error checking ready status: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def timeout(self, request, pk=None):
        """Handle when the game timer runs out"""
        try:
            session = self.get_object()
            profile = request.user.coding_profile
            
            # Check if user is a participant
            if not session.participants.filter(id=profile.id).exists():
                return Response(
                    {"detail": "Not a participant in this session"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Mark the session as ended
            session.is_active = False
            session.end_time = timezone.now()
            session.save()
            
            # Get leaderboard data
            leaderboard_data = self.get_leaderboard_data(session)
            
            # Determine the winner based on most problems solved
            winner = None
            max_solved = -1
            
            for participation in session.participations.all().order_by('-problems_solved', 'total_time'):
                if participation.problems_solved > max_solved:
                    max_solved = participation.problems_solved
                    winner = participation.profile
            
            # If no clear winner (tie or no problems solved), the winner is null
            winner_data = None
            if winner:
                winner_data = {
                    'id': winner.id,
                    'username': winner.user.username,
                    'display_name': winner.display_name
                }
            
            # Notify all participants about the timeout
            WebSocketManager.notify_session_update(
                str(session.id),
                'game_end', 
                {
                    'type': 'game_ended',
                    'timeout': True,
                    'winner': winner_data,
                    'leaderboard': leaderboard_data
                }
            )
            
            return Response({
                "detail": "Session ended due to timeout",
                "leaderboard": leaderboard_data,
                "winner": winner_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Error ending session: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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

    def coderunner(self, code, language, stdin=""):
        # File extensions mapping for different languages
        extensions = {
            'python': 'py',
            'python3': 'py',
            'javascript': 'js',
            'node': 'js',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'c': 'c',
            'csharp': 'cs',
            'c#': 'cs',
            'go': 'go',
            'golang': 'go',
            'rust': 'rs',
            'php': 'php',
            'ruby': 'rb',
            'kotlin': 'kt',
            'swift': 'swift',
            'typescript': 'ts',
            'ts': 'ts',
            'scala': 'scala',
            'perl': 'pl',
            'lua': 'lua',
            'r': 'r',
            'haskell': 'hs',
            'dart': 'dart',
            'elixir': 'ex',
            'julia': 'jl',
            'fortran': 'f90',
            'cobol': 'cob',
            'pascal': 'pas',
            'assembly': 'asm',
            'bash': 'sh',
            'shell': 'sh',
            'powershell': 'ps1'
        }
        
        # Prepare the API payload
        payload = {
            "language": language.lower(),
            "version": "3",
            "files": [
                {
                    "name": f"main.{extensions.get(language.lower(), 'txt')}",
                    "content": code
                }
            ],
            "stdin": stdin,
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": 3000,
            "compile_memory_limit": -1,
            "run_memory_limit": -1
        }
        
        try:
            # Make the API request to Piston
            response = requests.post(
                "https://emkc.org/api/v2/piston/execute",
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "PistonExecutor/1.0"
                },
                data=json.dumps(payload),
                timeout=30
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse and return the JSON response
            result = response.json()
            
            # Format the response for easier access
            formatted_result = {
                "language": result.get("language", ""),
                "version": result.get("version", ""),
                "stdout": result.get("run", {}).get("stdout", ""),
                "stderr": result.get("run", {}).get("stderr", ""),
                "code": result.get("run", {}).get("code", 0),
                "signal": result.get("run", {}).get("signal", None),
                "compile": result.get("compile", {}),
                "raw_response": result
            }
            
            print(formatted_result)
            return formatted_result
            
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout - execution took too long",
                "stdout": "",
                "stderr": "",
                "code": -1
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "Connection error - could not reach Piston API",
                "stdout": "",
                "stderr": "",
                "code": -1
            }
        except requests.exceptions.HTTPError as e:
            return {
                "error": f"HTTP error: {e.response.status_code} - {e.response.text}",
                "stdout": "",
                "stderr": "",
                "code": -1
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Request failed: {str(e)}",
                "stdout": "",
                "stderr": "",
                "code": -1
            }
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response from API",
                "stdout": "",
                "stderr": "",
                "code": -1
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "stdout": "",
                "stderr": "",
                "code": -1
            }

    @action(detail=True, methods=['post'])
    def submit(self, request, problem_id=None):
        """Submit a solution for a problem"""
        problem = get_object_or_404(CodingProblem, id=problem_id)
        profile = request.user.coding_profile
        
        # Get session_id from request data (optional)
        session_id = request.data.get('session_id')
        game_session = None
        
        # If session provided, validate it
        if session_id:
            game_session = get_object_or_404(GameSession, id=session_id)
            
            # Check if user is a participant in the session
            if not game_session.participants.filter(id=profile.id).exists():
                return Response(
                    {"detail": "Not a participant in this session"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
            # Check if session is active
            if not game_session.is_active or (game_session.end_time and game_session.end_time < timezone.now()):
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
            game_session=game_session
        )
        
        # Run the code with test cases if available
        try:
            # Get test cases from the problem
            testcases = problem.test_cases if hasattr(problem, 'test_cases') and problem.test_cases else []
            
            passed = 0

            for i in range(len(testcases)):
                # Prepare input if test cases are available
                stdin = ""

                if testcases and len(testcases) > 0 and 'input' in testcases[i]:
                    stdin = testcases[i]['input']
            
                # Run the code
                result = self.coderunner(
                    submission.code, 
                    submission.language,
                    stdin
                )
            
                # Basic status determination
                status_code = Submission.Status.ACCEPTED
                
                # Check for errors
                if result.get('error') or result.get('stderr'):
                    status_code = Submission.Status.RUNTIME_ERROR
                    if 'compile' in result and result['compile'].get('stderr'):
                        status_code = Submission.Status.COMPILATION_ERROR
            
                # Check test case output
                if status_code == Submission.Status.ACCEPTED and testcases and len(testcases) > 0:
                    expected = str(testcases[i].get('expected_output', '')).strip()
                    actual = str(result.get('stdout', '')).strip()
                    if expected == actual:
                        passed += 1
                    
                    else:
                        status_code = Submission.Status.WRONG_ANSWER
            
                # Update submission status
                submission.status = status_code
            
                # Add execution metrics if available
                time_taken = 0
                memory_used = 0
            
                if 'raw_response' in result and 'run' in result['raw_response']:
                    run_data = result['raw_response']['run']
                    time_taken = run_data.get('time', 0)
                    memory_used = run_data.get('memory', 0)
            
                submission.execution_time = time_taken
                submission.memory_usage = memory_used
                submission.save()

                # Format output for response
                output_data = {
                    "result": {
                        "status": submission.get_status_display(),
                        "error": result.get('error') or result.get('stderr') or "No errors",
                        "output": result.get('stdout', ''),
                        "time": f"{time_taken}s",
                        "memory": f"{memory_used}MB"
                    },
                    "submission_id": submission.id,
                    "passed": passed
                }
            
            # Add session data if part of a session
            if game_session:
                # Check if user solved all problems and passed all test cases
                session_ended = False
                leaderboard = None
                
                # Check if all test cases were passed
                if passed == len(testcases):
                    # Mark this user as the winner
                    participation = GameParticipation.objects.get(
                        game_session=game_session,
                        profile=profile
                    )
                    participation.problems_solved += 1
                    participation.score += 100  # Award points for solving
                    participation.save()
                    
                    # End the session
                    game_session.is_active = False
                    game_session.end_time = timezone.now()
                    game_session.save()

                    # Set session_ended to true and prepare leaderboard
                    session_ended = True
                    leaderboard = self.get_leaderboard_data(game_session)
                    
                    # Notify all participants about the winner
                    WebSocketManager.notify_session_update(
                        str(game_session.id),  # Convert to string to ensure proper formatting
                        'game_end', 
                        {
                            'type': 'game_ended',
                            'winner': {
                                'id': profile.id,
                                'username': profile.user.username,
                                'display_name': profile.display_name
                            },
                            'leaderboard': leaderboard
                        }
                    )
                
                # Add these to the response
                output_data["session_ended"] = session_ended
                output_data["winner"] = {
                    'id': profile.id,
                    'username': profile.user.username,
                    'display_name': profile.display_name
                } if session_ended else None
                
                if session_ended:
                    output_data["leaderboard"] = leaderboard
            
            print("\n\n-------------------------------------------------------------")
            print(passed)
            print("-------------------------------------------------------------\n\n")
            
            return Response(output_data)
            
        except Exception as e:
            # Log the error
            print(f"Error processing submission: {str(e)}")
            
            # Update submission status
            submission.status = Submission.Status.RUNTIME_ERROR
            submission.save()
            
            return Response({
                "result": {
                    "status": "Error",
                    "error": str(e),
                    "output": "",
                    "time": "0s",
                    "memory": "0MB"
                },
                "submission_id": submission.id
            })

@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        profile = request.user.coding_profile
        return Response(CodingProfileSerializer(profile).data)
    return Response(
        {"detail": "Not authenticated"}, 
        status=status.HTTP_401_UNAUTHORIZED
    )
