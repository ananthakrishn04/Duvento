from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

# Create your views here.
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
import random

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

def mainView(request):
    return render(request,"coding-grounds-app.html")


class BadgeView(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    queryset = Badge.objects.all()

class CodingProfileView(viewsets.ModelViewSet):
    serializer_class = CodingProfileSerializer
    queryset = CodingProfile.objects.all()

class CodingProblemView(viewsets.ModelViewSet):
    serializer_class = CodingProblemSerializer
    queryset = CodingProblem.objects.all()

# class SubmissionView(viewsets.ModelViewSet):
#     queryset = Submission.objects.all()
#     serializer_class = SubmissionSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         request_data = request.data.copy()
        
#         serializer = self.get_serializer(data=request_data)
#         serializer.is_valid(raise_exception=True)
        
#         profile = request.user.coding_profile
#         problem_id = serializer.validated_data.get('problem_id')
#         session_id = serializer.validated_data.get('session_id')
#         code = serializer.validated_data.get('code')
#         language = serializer.validated_data.get('language', 'python')
        
#         # Look up the problem and session
#         problem = get_object_or_404(CodingProblem, id=problem_id)
#         session = get_object_or_404(GameSession, id=session_id)
        
#         # Check permissions
#         if not session.participants.filter(id=profile.id).exists():
#             return Response({"detail": "Not a participant in this session"}, 
#                         status=status.HTTP_403_FORBIDDEN)
    
#         if not session.is_active or session.end_time < timezone.now():
#             return Response({"detail": "Session is not active"}, 
#                         status=status.HTTP_400_BAD_REQUEST)
        
#         # Create the submission directly instead of using serializer.save()
#         # This way we can provide the profile and problem objects directly
#         submission = Submission.objects.create(
#             profile=profile,
#             problem=problem,
#             code=code,
#             language=language,
#             game_session=session
#         )

#         # Run the code
#         result = self.coderunner(code, language)

#         # Update status based on result
#         if result["error"]:
#             submission.status = Submission.Status.WRONG_ANSWER
#             submission.save()

#             return Response({
#                 'submission': serializer.data,
#                 'result': result
#             }, status=status.HTTP_201_CREATED)
        
#         else:
#             submission.status = Submission.Status.ACCEPTED
#             submission.save()

#         self.notify_session_update(
#                 session_id,
#                 'end',
#                 {
#                     'type' : 'session_end',
#                     'detail' : "session has ended",
#                 }
#             )

#         participants_data = []
        
#         # Return a JSON response with the submission data and result
#         # return Response({
#         #     'submission': SubmissionSerializer(submission).data,
#         #     'result': result,
#         #     'redirect_url': reverse('game_session_status', kwargs={'session_id': session_id})
#         # }, status=status.HTTP_201_CREATED)

#         # if result["error"]:
#         #     if "compilation" in result["error"].lower():
#         #         submission.status = Submission.Status.COMPILATION_ERROR
#         #     elif "runtime" in result["error"].lower():
#         #         submission.status = Submission.Status.RUNTIME_ERROR
#         #     else:
#         #         submission.status = Submission.Status.WRONG_ANSWER

#         # elif result["time"] and float(result["time"]) > problem.time_limit:
#         #     submission.status = Submission.Status.TIME_LIMIT_EXCEEDED
#         # elif result["memory"] and float(result["memory"]) > problem.memory_limit:
#         #     submission.status = Submission.Status.MEMORY_LIMIT_EXCEEDED
#         #     submission.status = Submission.Status.WRONG_ANSWER

#         #     
#         #     return Response({
#         #     'submission': serializer.data,
#         #     'result': result
#         #     }, status=status.HTTP_201_CREATED)
        
#         # else:
#         #     if self.validate_output(result["output"], problem.test_cases):
#         #         submission.status = Submission.Status.ACCEPTED
#         #     else:
#         #         submission.status = Submission.Status.WRONG_ANSWER

        

#         return Response({
#             'submission': serializer.data,
#             'result': result
#         }, status=status.HTTP_201_CREATED)

#     def coderunner(self, source_code, language):
#         # Judge0 API endpoint
#         JUDGE0_API_URL = "http://192.168.1.8:2358"
#         SUBMISSION_URL = f"{JUDGE0_API_URL}/submissions"

#         lanugageMap = {
#             "python" : 71,
#             "javascript" : 63,
#             "java" : 62
#         }

#         # Prepare the request payload with CPU and memory limits
#         data = {
#             "source_code": source_code,
#             "language_id": lanugageMap[language],
#             "cpu_time_limit": 2,  # Max execution time in seconds
#             "memory_limit": 128000,  # Max memory in KB (128MB)
#         }

#         # # Submit the code
#         # response = requests.post(SUBMISSION_URL, json=data)
#         # token = response.json().get("token")

#         # if not token:
#         #     print("Failed to get submission token.")
#         #     exit()

#         # # Fetch the result
#         # RESULT_URL = f"{SUBMISSION_URL}/{token}"
#         # while True:
#         #     result = requests.get(RESULT_URL).json()
#         #     if result["status"]["id"] in [1, 2]:  # Queued or Processing
#         #         # time.sleep(1)
#         #         pass
#         #     else:
#         #         break

#         # Print the output
#         # return {
#         #     "output" : result.get("stdout", "No output"),
#         #     "error" : result.get("stderr", "No errors"),
#         #     "status" : result["status"]["description"],
#         #     "time" : str(result["time"]) + "s",
#         #     "memory" : str(result["memory"]) + "KB"
#         # }

#         return {
#             "output" : "",
#             "error" : None,
#             "status" : "",
#             "time" : "",
#             "memory" : ""
#         }
#     def notify_session_update(self, session_id, event_type, data):
#         channel_layer = get_channel_layer()
#         group_name = f'session_{session_id}'
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 'type': f'session_{event_type}',
#                 'message': data
#             }
#         )

class SubmissionView(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        
        profile = request.user.coding_profile
        problem_id = serializer.validated_data.get('problem_id')
        session_id = serializer.validated_data.get('session_id')
        code = serializer.validated_data.get('code')
        language = serializer.validated_data.get('language', 'python')
        
        # Look up the problem and session
        problem = get_object_or_404(CodingProblem, id=problem_id)
        session = get_object_or_404(GameSession, id=session_id)
        
        # Check permissions
        if not session.participants.filter(id=profile.id).exists():
            return Response({"detail": "Not a participant in this session"}, 
                        status=status.HTTP_403_FORBIDDEN)
    
        if not session.is_active or (session.end_time and session.end_time < timezone.now()):
            return Response({"detail": "Session is not active"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # Create the submission
        submission = Submission.objects.create(
            profile=profile,
            problem=problem,
            code=code,
            language=language,
            game_session=session
        )

        # Run the code
        result = self.coderunner(code, language)

        # Update submission status based on result
        if result["error"]:
            submission.status = Submission.Status.WRONG_ANSWER
        else:
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
                
                # If all problems are solved, update leaderboard
                session_problems_count = session.problems.count()
                if participation.problems_solved >= session_problems_count:
                    # Check if this is the first participant to solve all problems
                    all_solved_count = GameParticipation.objects.filter(
                        game_session=session,
                        problems_solved__gte=session_problems_count
                    ).count()
                    
                    # If this is the first participant to solve all problems, end the session
                    if all_solved_count == 1:
                        session.end_session()
                        # Notify all participants of session end
                        self.notify_session_update(
                            session_id,
                            'end',
                            {
                                'type': 'session_end',
                                'detail': "Session has ended - all problems solved!",
                                'winner': profile.display_name
                            }
                        )  
                        
        # Save the updated submission
        submission.save()
        
        # Update user profile
        profile.update_streak()
        
        # Prepare participants data for leaderboard
        participants_data = []
        for participation in session.participations.all().order_by('-problems_solved', 'total_time'):
            minutes, seconds = divmod(participation.total_time, 60)
            formatted_time = f"{minutes:02d}:{seconds:02d}"
            
            # Create serializable participant data
            participant_data = {
                'profile_id': participation.profile.id,
                'username': participation.profile.display_name,
                'problems_solved': participation.problems_solved,
                'total_time': participation.total_time,
                'formatted_time': formatted_time,
                'score': participation.score
            }
            participants_data.append(participant_data)
        
        # Notify all participants of leaderboard update
        self.notify_session_update(
            session_id,
            'leaderboard',
            {
                'type': 'leaderboard_status',
                'leaderboard': participants_data
            }
        )

        return Response({
            'submission': SubmissionSerializer(submission).data,
            'result': result,
            'leaderboard': participants_data
        }, status=status.HTTP_201_CREATED)

    def coderunner(self, source_code, language):
        # Judge0 API endpoint
        JUDGE0_API_URL = "http://192.168.1.8:2358"
        SUBMISSION_URL = f"{JUDGE0_API_URL}/submissions"

        languageMap = {
            "python": 71,
            "javascript": 63,
            "java": 62
        }

        # Prepare the request payload with CPU and memory limits
        data = {
            "source_code": source_code,
            "language_id": languageMap[language],
            "cpu_time_limit": 2,  # Max execution time in seconds
            "memory_limit": 128000,  # Max memory in KB (128MB)
        }

        # Your existing code runner implementation here
        # For now, we'll use your placeholder response

        return {
            "output": "",
            "error": None,
            "status": "Accepted",
            "time": "0.3 s",
            "memory": "100 KB"
        }

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


class GameSessionView(viewsets.ModelViewSet):
    # serializer_class = GameSessionSerializer
    queryset = GameSession.objects.filter(is_active=True)
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        profile = request.user.coding_profile

        # serializer = self.get_serializer(data=request.data)

        # session = serializer.save(created_by=profile)

        session = GameSession.objects.create(
            title = request.data.get("title"),
            is_private = request.data.get("is_private"),
            max_participants = request.data.get("max_participants"),
            access_code = request.data.get("access_code" , ""),
            created_by = profile
        )

        problem = random.choice(list(CodingProblem.objects.all()))
        session.problems.add(problem)
        session.add_participant(profile)
        session.save()

        return Response({"id": session.id,"detail" : "session created successfully"})
    
    
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

            self.update_participants(session=session)

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

        self.update_participants(session=session)
        
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

        self.update_participants(session=session)
        
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
        
        problems = list(session.problems.all())

        editor_url = f"/editor?problem_id={problems[0].id}&session_id={session.id}"

        # Start the session
        if session.start_if_ready():
            self.notify_session_update(
                session.id, 
                'start',
                {
                    'type': 'start',
                    'detail' : 'session_started',
                    'redirect_url': editor_url
                }
            )

            return Response({"status":"started","detail": "Session started successfully"}, 
                            status=status.HTTP_200_OK)
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

        user_profile = request.user.coding_profile
        is_participant = session.participants.filter(id=user_profile.id).exists()
        is_creator = session.created_by == user_profile
        
        if not (is_participant or is_creator):
            return render(request, 'error.html', {
                'message': 'You do not have permission to view this session.'
            })
        
        participants_data = []
        
        for participation in session.participations.all().order_by('-problems_solved', 'total_time'):
            # Get the last submission for this participant in this session
            last_submission = Submission.objects.filter(
                profile=participation.profile,
                game_session=session
            ).order_by('-submitted_at').first()
            
            # Format time for display (convert seconds to MM:SS format)
            minutes, seconds = divmod(participation.total_time, 60)
            formatted_time = f"{minutes:02d}:{seconds:02d}"
            
            participants_data.append({
                'profile_id': participation.profile.id,
                'username': participation.profile.display_name,
                'problems_solved': participation.problems_solved,
                'total_time': participation.total_time,
                'formatted_time': formatted_time,
                'minutes_taken': minutes,
                'seconds_taken': seconds,
                'final_rank': participation.final_rank,
                'score': participation.score,
                'is_ready': participation.is_ready,
            })
        
        self.notify_session_update(
            session.id,
            'leaderboard',
            {
                'type' : 'leaderboard_status',
                'participant_status' : participants_data
            }
        )

        context = {
            'participants_data' : participants_data
        }

        return render(request, 'game_status.html', context)
    
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
    
    def update_participants(self,session):
        participants_data = list(GameParticipation.objects.filter(game_session=session).values(
            'profile__id', 
            'profile__display_name',  
            'is_ready'
        ))


        self.notify_session_update(
                session.id, 
                'participant_update',
                {
                    'type': 'participant_update',
                    'participants' : participants_data
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


@api_view(['GET'])
def code_editor_view(request):
    problem_id = request.GET.get('problem_id')
    session_id = request.GET.get('session_id')

    if not problem_id or not session_id:
        return HttpResponse("Problem ID and Session ID are required", status=400)

    # Check if problem and session exist
    try:
        problem = CodingProblem.objects.get(id=problem_id)
        session = GameSession.objects.get(id=session_id)
    except (CodingProblem.DoesNotExist, GameSession.DoesNotExist):
        return HttpResponse("Problem or Session not found", status=404)

    # Return the code editor template
    return render(request, 'code_editor_new.html', {
        'problem': problem,
        'session': session,
        'participants' : session.participants.all()
    })
