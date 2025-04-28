from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import (
    CodingProfile,
    CodingProblem,
    GameSession,
    Badge,
    Submission,
    GameParticipation
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class CodingProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)
    
    class Meta:
        model = CodingProfile
        fields = [
            'id', 'user', 'username', 'password', 'display_name','email','rating', 
            'problems_solved', 'rank', 'bio', 'avatar', 'streak', 
            'joined_at', 'last_activity'
        ]
        read_only_fields = [
            'id', 'rating', 'problems_solved', 'rank', 
            'streak', 'joined_at', 'last_activity'
        ]
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered.")
        return value
    
    def create(self, validated_data):
        # Extract user data
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        
        if 'display_name' not in validated_data or not validated_data['display_name']:
            validated_data['display_name'] = username
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile
        profile = CodingProfile.objects.create(
            user=user,
            **validated_data
        )
        
        return profile

class CodingProblemSerializer(serializers.ModelSerializer):
    difficulty = serializers.SerializerMethodField()
    
    class Meta:
        model = CodingProblem
        fields = [
            'id', 'title', 'description', 'difficulty', 'created_by',
            'time_limit', 'memory_limit', 'test_cases', 'tags'
        ]
        read_only_fields = ['id']

    def get_difficulty(self, obj):
        return obj.Difficulty(obj.difficulty).label

class GameSessionSerializer(serializers.ModelSerializer):
    created_by = CodingProfileSerializer(read_only=True)
    participants = CodingProfileSerializer(many=True, read_only=True)
    problems = CodingProblemSerializer(many=True, read_only=True)
    
    class Meta:
        model = GameSession
        fields = [
            'id', 'title', 'created_by', 'is_private', 
            'max_participants', 'access_code', 'is_active',
            'start_time', 'end_time', 'participants', 'problems'
        ]
        read_only_fields = ['id', 'start_time', 'end_time']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon']
        read_only_fields = ['id']

class SubmissionSerializer(serializers.ModelSerializer):
    profile = CodingProfileSerializer(read_only=True)
    problem = CodingProblemSerializer(read_only=True)
    game_session = GameSessionSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'profile', 'problem', 'code', 'language',
            'status', 'submitted_at', 'game_session'
        ]
        read_only_fields = ['id', 'profile', 'submitted_at', 'status']

class GameParticipationSerializer(serializers.ModelSerializer):
    profile = CodingProfileSerializer(read_only=True)
    session = GameSessionSerializer(read_only=True)
    
    class Meta:
        model = GameParticipation
        fields = [
            'id', 'profile', 'session', 'problems_solved',
            'total_time', 'score', 'is_ready', 'final_rank'
        ]
        read_only_fields = ['id', 'profile', 'session', 'final_rank']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include username and password.")
