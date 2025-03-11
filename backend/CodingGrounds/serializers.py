from rest_framework import serializers

from .models import GameSession, Badge, CodingProblem, CodingProfile, Submission, GameParticipation

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = "__all__"

# class GameSessionSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='title', required=True)
    
#     class Meta:
#         model = GameSession
#         fields = [
#             'id', 'title', 'name', 'description', 
#             'is_active', 'created_by', 'max_participants', 
#             'is_private', 'access_code'
#         ]
#         extra_kwargs = {
#             'created_by': {'required': False},
#             'title': {'required': True},
#             'is_private': {'required': False},
#             'max_participants': {'required': False}
#         }

#     def validate(self, data):
#         # Explicit validation
#         if data.get('is_private', False) and not data.get('access_code'):
#             raise serializers.ValidationError({
#                 'access_code': 'Access code is required for private sessions'
#             })
        
#         # Ensure title is not empty
#         if not data.get('title'):
#             raise serializers.ValidationError({
#                 'title': 'Session name cannot be empty'
#             })
        
#         return data

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class CodingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingProfile
        fields = ['id', 'username', 'email', 'display_name', 'rating', 'problems_solved', 
                 'rank', 'bio', 'avatar', 'streak', 'joined_at', 'last_activity']
        read_only_fields = ['id', 'rating', 'problems_solved', 'rank', 'streak', 
                           'joined_at', 'last_activity']

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'password']
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'email': {'required': True}
#         }

class CodingProblemSerializer(serializers.ModelSerializer):
    difficulty = serializers.CharField(source='get_difficulty_display')
    class Meta:
        model = CodingProblem
        fields = ['id','title','description','difficulty','test_cases','time_limit','memory_limit','tags']

# class SubmissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Submission
#         fields = '__all__'
#         read_only_fields = ['status','execution_time','memory_usage']

class SubmissionSerializer(serializers.ModelSerializer):
    problem_id = serializers.IntegerField(write_only=True)
    session_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'status', 'execution_time', 'memory_usage', 'submitted_at', 
                  'problem_id', 'session_id', 'code', 'language']
        read_only_fields = ['profile', 'problem', 'status', 'execution_time', 'memory_usage', 'submitted_at']
        
class GameParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipation
        fields = '__all__'
