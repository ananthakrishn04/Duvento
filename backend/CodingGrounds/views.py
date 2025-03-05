from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone

# Create your views here.
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .models import GameSession, Badge, CodingProfile, CodingProblem, Submission, GameParticipation

from .serializers import (
    BadgeSerializer,
    CodingProfileSerializer,
    CodingProblemSerializer,
    SubmissionSerializer,
    GameSessionSerializer,
    GameParticipationSerializer,
)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class BadgeView(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    queryset = Badge.objects.all()

class CodingProfileView(viewsets.ModelViewSet):
    serializer_class = CodingProfileSerializer
    queryset = CodingProfile.objects.all()

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     # username = data.get('username')
    #     # email = data.get('email')
    #     password = data.get('password')  # Make sure password is included in the request
        
    #     # Create the Django User and connect it to the profile

    #     if password:
    #     # Create the CodingProfile first
    #         serializer = self.get_serializer(data=data)
    #         if serializer.is_valid():
    #             profile = serializer.save()
            
    #             user = profile.create_auth_user(password)
    #             # Return both profile and user info
    #             return Response({
    #                 'profile': serializer.data,
    #                 'user_created': True,
    #                 'username': user.username
    #             }, status=status.HTTP_201_CREATED)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({
    #             'profile':None,
    #             'user_created': False,
    #             'error': 'Password is required to create a user'
    #         }, status=status.HTTP_206_PARTIAL_CONTENT)
        
        

class CodingProblemView(viewsets.ModelViewSet):
    serializer_class = CodingProblemSerializer
    queryset = CodingProblem.objects.all()

class SubmissionView(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        profile = self.request.user.coding_profile
        problem_id = self.request.data.get('problem_id')
        session_id = self.request.data.get('session_id')
        
        problem = get_object_or_404(CodingProblem, id=problem_id)
        session = get_object_or_404(GameSession, id=session_id)
        
        # Check if user is a participant
        if not session.participants.filter(id=profile.id).exists():
            return Response({"detail": "Not a participant in this session"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Check if session is active
        if not session.is_active or session.end_time < timezone.now():
            return Response({"detail": "Session is not active"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Create submission
        serializer.save(
            profile=profile,
            problem=problem,
            game_session=session
        )

class GameSessionView(viewsets.ModelViewSet):
    # serializer_class = GameSessionSerializer
    queryset = GameSession.objects.filter(is_active=True)
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        profile = self.request.user.coding_profile
        session = serializer.save(created_by=profile)
        # Automatically add creator as participant
        session.add_participant(profile)
        print("Request Data:", self.request.data)
        # print("Validated Data:", serializer.validated_data)

        # try:
        #     session = serializer.save(created_by=profile)
        #     session.add_participant(profile)
        # except Exception as e:
        #     print(f"Session Creation Error: {str(e)}")
        #     raise

    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a game session"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        # Check if session is full
        if session.max_participants > 0 and session.participants.count() >= session.max_participants:
            return Response({"detail": "Session is full"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if session is private and requires access code
        if session.is_private:
            access_code = request.data.get('access_code')
            if access_code != session.access_code:
                return Response({"detail": "Invalid access code"}, status=status.HTTP_403_FORBIDDEN)
        
        if session.add_participant(profile):
            self.notify_session_update(
                session.id, 
                'user_join',
                {
                    'type': 'user_join',
                    'user': {
                        'id': profile.id,
                        'username': profile.display_name,
                        # Add other user fields you want to expose
                    }
                }
            )

            serializer = self.get_serializer(session)

            return Response({"detail": "Joined session successfully","session":serializer.data})
        else:
            return Response({"detail": "Already a participant"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a game session"""
        session = self.get_object()
        profile = request.user.coding_profile
        session.remove_participant(profile)
        self.notify_session_update(
            session.id, 
            'user_leave',
            {
                'type': 'user_leave',
                'user': {
                    'id': profile.id,
                    'username': profile.display_name,
                    # Add other user fields you want to expose
                }
            }
        )
        return Response({"detail": "Left session successfully"})
    
    @action(detail=True, methods=['post'])
    def ready(self, request, pk=None):
        """Mark yourself as ready to start"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        participation = get_object_or_404(
            GameParticipation, 
            game_session=session,
            profile=profile
        )
        participation.is_ready = True
        participation.save()
        
        # Check if all participants are ready
        all_ready = session.all_participants_ready()

        self.notify_session_update(
            session.id, 
            'ready_status',
            {
                'type': 'ready_status',
                'user': {
                    'id': profile.id,
                    'username': profile.display_name,
                    # Add other user fields you want to expose
                },
                'all_ready':all_ready,
            }
        )
        
        return Response({
            "is_ready": True,
            "all_ready": all_ready
        })
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the game session (only creator can do this)"""
        session = self.get_object()
        profile = request.user.coding_profile
        
        # Only creator can start
        if session.created_by != profile:
            return Response({"detail": "Only the creator can start the session"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Check if all participants are ready
        if not session.all_participants_ready():
            return Response({"detail": "Not all participants are ready"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Start the session
        if session.start_if_ready():
            self.notify_session_update(
                session.id, 
                'start',
                {
                    'type': 'start',
                    'detail' : 'session_started'
                }
            )
            return Response({"status":"started","detail": "Session started successfully"})
        else:
            return Response({"detail": "Unable to start session"}, 
                           status=status.HTTP_400_BAD_REQUEST)
    
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
        
        participations = session.participations.all()
        serializer = GameParticipationSerializer(participations, many=True)
        return Response(serializer.data)
    
    def notify_session_update(self, session_id, event_type, data):
        channel_layer = get_channel_layer()
        group_name = f'session_{session_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': f'session_{event_type}',
                'message': data
            }
        )


class GameParticipationView(viewsets.ModelViewSet):
    serializer_class = GameParticipationSerializer
    queryset = GameParticipation.objects.all()


class SolveProblemView(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    lookup_field = "problem_id"

    def create(self, request, *args, **kwargs):
        """Handles submission and participation when users submit a solution."""
        problem_id = kwargs.get("problem_id")
        problem = get_object_or_404(CodingProblem, id=problem_id)
        user = request.user  # Assuming user has a CodingProfile

        # Preparing submission data
        data = {
            "user": user.id,
            "problem": problem.id,
            "code": request.data.get("code", ""),
            "status": "Pending",
        }

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            submission = serializer.save()

            # Log participation
            participation_data = {
                "user": user.id,
                "session": None,  # Associate with a session if needed
                "problem": problem.id,
                "submission": submission.id,
            }
            participation_serializer = GameParticipationSerializer(data=participation_data)
            if participation_serializer.is_valid():
                participation_serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def problem_details(self, request, problem_id=None):
        """Retrieve problem details for solving."""
        problem = get_object_or_404(CodingProblem, id=problem_id)
        return Response(
            {
                "title": problem.title,
                "description": problem.description,
                "difficulty": problem.get_difficulty_display(),
                "time_limit": problem.time_limit,
                "memory_limit": problem.memory_limit,
                "tags": problem.tags,
            }
        )

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # First create the CodingProfile without user
        profile_data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'display_name': request.data.get('display_name', request.data.get('username')),
            'bio': request.data.get('bio', ''),
            'avatar': request.data.get('avatar', '')
        }
        
        # Validate profile data
        profile_serializer = CodingProfileSerializer(data=profile_data)
        if not profile_serializer.is_valid():
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create profile
        profile = profile_serializer.save()
        
        # Create auth user linked to profile
        password = request.data.get('password')
        if not password:
            profile.delete()
            return Response({"password": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = profile.create_auth_user(password)
        except Exception as e:
            profile.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'profile_id': profile.id,
            'username': profile.username,
            'display_name': profile.display_name,
            'email': profile.email,
            'rating': profile.rating,
            'rank': profile.rank
        }, status=status.HTTP_201_CREATED)


class UserLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        try:
            profile = CodingProfile.objects.get(user=user)
            
            # Update last_activity
            profile.last_activity = timezone.now()
            profile.save()
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'profile_id': profile.id,
                'username': profile.username,
                'display_name': profile.display_name,
                'email': profile.email,
                'rating': profile.rating,
                'rank': profile.rank
            })
        except CodingProfile.DoesNotExist:
            return Response({
                'token': token.key,
                'user_id': user.id,
                'error': 'No coding profile found for this user'
            })


@api_view(['GET'])
def current_user(request):
    """
    Get information about the currently authenticated user
    """
    if not request.user.is_authenticated:
        return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        profile = CodingProfile.objects.get(user=request.user)
        
        # Update last_activity
        profile.last_activity = timezone.now()
        profile.save()
        
        return Response({
            'user_id': request.user.id,
            'profile_id': profile.id,
            'username': profile.username,
            'display_name': profile.display_name,
            'email': profile.email,
            'rating': profile.rating,
            'problems_solved': profile.problems_solved,
            'rank': profile.rank,
            'bio': profile.bio,
            'avatar': profile.avatar,
            'streak': profile.streak,
            'joined_at': profile.joined_at,
            'last_activity': profile.last_activity
        })
    except CodingProfile.DoesNotExist:
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'error': 'No coding profile found for this user'
        })