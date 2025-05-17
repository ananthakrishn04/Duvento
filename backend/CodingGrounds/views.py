from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

import requests
import random

# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, BasePermission
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    GameSession, Badge, CodingProfile, CodingProblem, Submission, GameParticipation,
    League, LeagueParticipation, LeagueMatch, CodingProfile, GameSession
)

from .serializers import (
    BadgeSerializer,
    CodingProfileSerializer,
    CodingProblemSerializer,
    SubmissionSerializer,
    GameSessionSerializer,
    GameParticipationSerializer,
    UserLoginSerializer,
    LeagueSerializer, 
    LeagueDetailSerializer, 
    LeagueParticipationSerializer, 
    LeagueMatchSerializer
)

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
            Q(created_by=profile) | 
            Q(participants=profile)
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

    def coderunner(self, source_code, language, test_cases, time_limit=2.0, memory_limit=128):
        """
        Send code to the execution service and get results
        """
        try:
            # Get code execution service URL from settings or use default
            code_execution_url = getattr(settings, 'CODE_EXECUTION_URL', 'http://localhost:8000')
            
            # Prepare the request payload
            payload = {
                "source_code": source_code,
                "language": language,
                "test_cases": test_cases,
                "time_limit": time_limit,
                "memory_limit": memory_limit
            }
            
            # Send the request to the code execution service
            response = requests.post(
                f"{code_execution_url}/execute",
                json=payload,
                timeout=30  # Reasonable timeout for code execution
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result_data = response.json()
                return result_data["results"]
            else:
                # Log the error
                print(f"Code execution service error: {response.status_code} - {response.text}")
                # Return a generic error
                return [{
                    "test_case": 1,
                    "output": "",
                    "expected": "",
                    "match": False,
                    "error": f"Code execution service error: {response.status_code}",
                    "status": Submission.Status.RUNTIME_ERROR,
                    "time": "0.00s",
                    "memory": "0MB"
                }]
                
        except requests.RequestException as e:
            # Handle connection errors
            print(f"Connection error: {str(e)}")
            return [{
                "test_case": 1,
                "output": "",
                "expected": "",
                "match": False,
                "error": f"Connection error: {str(e)}",
                "status": Submission.Status.RUNTIME_ERROR,
                "time": "0.00s",
                "memory": "0MB"
            }]

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
        
        # Run the code using our real coderunner
        result = self.coderunner(
            submission.code, 
            submission.language, 
            problem.test_cases,
            problem.time_limit,
            problem.memory_limit
        )

        # Update submission status based on result
        all_accepted = all(r['status'] == Submission.Status.ACCEPTED for r in result)
        if all_accepted:
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
            # Determine the status based on the results
            if any(r['status'] == Submission.Status.COMPILATION_ERROR for r in result):
                submission.status = Submission.Status.COMPILATION_ERROR
            elif any(r['status'] == Submission.Status.RUNTIME_ERROR for r in result):
                submission.status = Submission.Status.RUNTIME_ERROR
            elif any(r['status'] == Submission.Status.TIME_LIMIT_EXCEEDED for r in result):
                submission.status = Submission.Status.TIME_LIMIT_EXCEEDED
            elif any(r['status'] == Submission.Status.MEMORY_LIMIT_EXCEEDED for r in result):
                submission.status = Submission.Status.MEMORY_LIMIT_EXCEEDED
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

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a league to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the league creator
        return obj.created_by == request.user.coding_profile


class LeagueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing leagues.
    """
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LeagueDetailSerializer
        return LeagueSerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned leagues based on query parameters,
        by filtering against 'status', 'active', or user's participation.
        """
        queryset = League.objects.all()
        
        # Apply filters based on query parameters
        status = self.request.query_params.get('status')
        is_active = self.request.query_params.get('active')
        my_leagues = self.request.query_params.get('my_leagues')
        
        if status:
            queryset = queryset.filter(status=status)
            
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter for current user's leagues if requested and authenticated
        if my_leagues and self.request.user.is_authenticated:
            profile = self.request.user.coding_profile
            queryset = queryset.filter(
                Q(created_by=profile) | Q(participants=profile)
            ).distinct()
        
        # Don't show private leagues unless they're the user's
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_private=False)
        else:
            profile = self.request.user.coding_profile
            queryset = queryset.filter(
                Q(is_private=False) | 
                Q(created_by=profile) | 
                Q(participants=profile)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the current user's profile as the creator of the league"""
        serializer.save(created_by=self.request.user.coding_profile)
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Register the current user to participate in the league"""
        league = self.get_object()
        profile = request.user.coding_profile
        
        # Check if access code is required and provided
        if league.is_private and league.access_code:
            provided_code = request.data.get('access_code')
            if not provided_code or provided_code != league.access_code:
                return Response(
                    {"detail": "Invalid access code"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        success, message = league.add_participant(profile)
        
        if success:
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        """Unregister the current user from the league"""
        league = self.get_object()
        profile = request.user.coding_profile
        
        success, message = league.remove_participant(profile)
        
        if success:
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, pk=None):
        """Start the league and create first round matchups"""
        league = self.get_object()
        
        # Only the league creator can start it
        if league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can start the league"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success, message = league.start_league()
        
        if success:
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def advance_round(self, request, pk=None):
        """Advance the league to the next round"""
        league = self.get_object()
        
        # Only the league creator can advance rounds
        if league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can advance rounds"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success, message = league.advance_round()
        
        if success:
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel the league"""
        league = self.get_object()
        
        # Only the league creator can cancel it
        if league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can cancel the league"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if league.status in ['completed', 'cancelled']:
            return Response(
                {"detail": "Cannot cancel a completed or already canceled league"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        league.status = 'cancelled'
        league.is_active = False
        league.end_date = timezone.now()
        league.save()
        
        return Response(
            {"detail": "League cancelled successfully"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_problem(self, request, pk=None):
        """Add a problem to the league"""
        league = self.get_object()
        
        # Only the league creator can add problems
        if league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can add problems"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot add problems after league has started
        if league.status not in ['pending', 'registration']:
            return Response(
                {"detail": "Cannot add problems after league has started"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        problem_id = request.data.get('problem_id')
        if not problem_id:
            return Response(
                {"detail": "Problem ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .models import CodingProblem
        try:
            problem = CodingProblem.objects.get(id=problem_id)
            league.problems.add(problem)
            return Response(
                {"detail": "Problem added successfully"},
                status=status.HTTP_200_OK
            )
        except CodingProblem.DoesNotExist:
            return Response(
                {"detail": "Problem not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_problem(self, request, pk=None):
        """Remove a problem from the league"""
        league = self.get_object()
        
        # Only the league creator can remove problems
        if league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can remove problems"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot remove problems after league has started
        if league.status not in ['pending', 'registration']:
            return Response(
                {"detail": "Cannot remove problems after league has started"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        problem_id = request.data.get('problem_id')
        if not problem_id:
            return Response(
                {"detail": "Problem ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .models import CodingProblem
        try:
            problem = CodingProblem.objects.get(id=problem_id)
            if problem in league.problems.all():
                league.problems.remove(problem)
                return Response(
                    {"detail": "Problem removed successfully"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Problem not in league"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except CodingProblem.DoesNotExist:
            return Response(
                {"detail": "Problem not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class LeagueMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing league matches.
    """
    queryset = LeagueMatch.objects.all()
    serializer_class = LeagueMatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Optionally restricts the returned matches to those belonging
        to a specific league or round.
        """
        queryset = LeagueMatch.objects.all()
        
        # Filter by league if provided
        league_id = self.request.query_params.get('league')
        if league_id:
            queryset = queryset.filter(league__id=league_id)
        
        # Filter by round if provided
        round_number = self.request.query_params.get('round')
        if round_number:
            queryset = queryset.filter(round_number=round_number)
        
        # Filter by participant if provided
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(
                Q(participant1__id=participant_id) | Q(participant2__id=participant_id)
            )
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join_game(self, request, pk=None):
        """Join the game session for this match"""
        match = self.get_object()
        profile = request.user.coding_profile
        
        # Check if user is a participant in this match
        if profile != match.participant1 and profile != match.participant2:
            return Response(
                {"detail": "You are not a participant in this match"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the match has a game session
        if not match.game_session:
            return Response(
                {"detail": "No game session available for this match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return the game session ID for the frontend to redirect
        return Response({
            "game_session_id": str(match.game_session.id)
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def determine_winner(self, request, pk=None):
        """Manually determine the winner of this match"""
        match = self.get_object()
        
        # Only league creator can manually set winners
        if match.league.created_by != request.user.coding_profile:
            return Response(
                {"detail": "Only the league creator can manually determine winners"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        winner_id = request.data.get('winner_id')
        if not winner_id:
            return Response(
                {"detail": "Winner ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate winner is a participant
        if (str(match.participant1.id) != winner_id and 
            str(match.participant2.id) != winner_id):
            return Response(
                {"detail": "Specified winner is not a participant in this match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set the winner
        winner = CodingProfile.objects.get(id=winner_id)
        match.winner = winner
        match.status = 'completed'
        match.save()
        
        return Response(
            {"detail": f"{winner.display_name} set as the winner"},
            status=status.HTTP_200_OK
        )


class LeagueParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing league participations.
    """
    queryset = LeagueParticipation.objects.all()
    serializer_class = LeagueParticipationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Optionally filters participations by league or profile.
        """
        queryset = LeagueParticipation.objects.all()
        
        # Filter by league if provided
        league_id = self.request.query_params.get('league')
        if league_id:
            queryset = queryset.filter(league__id=league_id)
        
        # Filter by profile if provided
        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(profile__id=profile_id)
            
        # Filter by current user if requested
        my_participations = self.request.query_params.get('my_participations')
        if my_participations and self.request.user.is_authenticated:
            profile = self.request.user.coding_profile
            queryset = queryset.filter(profile=profile)
        
        return queryset

@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        profile = request.user.coding_profile
        return Response(CodingProfileSerializer(profile).data)
    return Response(
        {"detail": "Not authenticated"}, 
        status=status.HTTP_401_UNAUTHORIZED
    )
