from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import (
    CodingProfile, CodingProblem, GameSession, Badge, Submission, GameParticipation,
    League, LeagueParticipation, LeagueMatch, CodingProfile, GameSession
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


class LeagueSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    current_round_display = serializers.SerializerMethodField()
    current_user_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = League
        fields = [
            'id', 'title', 'description', 'created_at', 'start_date', 'end_date',
            'is_active', 'max_participants', 'created_by', 'status', 'format',
            'session_duration', 'current_round', 'total_rounds', 'created_by_name',
            'participant_count', 'current_round_display', 'current_user_registered',
            'is_private'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by', 'participant_count', 
            'current_round_display', 'current_user_registered'
        ]
    
    def get_created_by_name(self, obj):
        return obj.created_by.display_name if obj.created_by else None
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_current_round_display(self, obj):
        if obj.status == 'completed':
            return "Completed"
        elif obj.status == 'registration':
            return "Registration Open"
        elif obj.status == 'cancelled':
            return "Cancelled"
        else:
            return f"Round {obj.current_round} of {obj.total_rounds}"
    
    def get_current_user_registered(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            profile = request.user.coding_profile
            return obj.participants.filter(id=profile.id).exists()
        return False

class LeagueDetailSerializer(LeagueSerializer):
    """Detailed league serializer including participants and matches"""
    participants = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    
    class Meta(LeagueSerializer.Meta):
        fields = LeagueSerializer.Meta.fields + ['participants', 'matches']
    
    def get_participants(self, obj):
        participations = LeagueParticipation.objects.filter(league=obj)
        return [
            {
                'id': p.profile.id,
                'display_name': p.profile.display_name,
                'rating': p.profile.rating,
                'avatar': p.profile.avatar,
                'registration_date': p.registration_date,
                'is_admin': p.is_admin,
                'final_rank': p.final_rank
            }
            for p in participations
        ]
    
    def get_matches(self, obj):
        matches = LeagueMatch.objects.filter(league=obj)
        return [
            {
                'id': m.id,
                'round': m.round_number,
                'match_number': m.match_number,
                'participant1': {
                    'id': m.participant1.id,
                    'display_name': m.participant1.display_name,
                },
                'participant2': {
                    'id': m.participant2.id,
                    'display_name': m.participant2.display_name,
                },
                'winner': m.winner.display_name if m.winner else None,
                'status': m.status,
                'game_session_id': str(m.game_session.id) if m.game_session else None,
                'scheduled_time': m.scheduled_time
            }
            for m in matches
        ]

class LeagueParticipationSerializer(serializers.ModelSerializer):
    profile_name = serializers.SerializerMethodField()
    league_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LeagueParticipation
        fields = [
            'id', 'league', 'profile', 'registration_date', 
            'is_active', 'final_rank', 'score', 'is_admin',
            'profile_name', 'league_title'
        ]
        read_only_fields = ['id', 'registration_date', 'final_rank', 'score']
    
    def get_profile_name(self, obj):
        return obj.profile.display_name
    
    def get_league_title(self, obj):
        return obj.league.title

class LeagueMatchSerializer(serializers.ModelSerializer):
    participant1_name = serializers.SerializerMethodField()
    participant2_name = serializers.SerializerMethodField()
    winner_name = serializers.SerializerMethodField()
    league_title = serializers.SerializerMethodField()
    
    class Meta:
        model = LeagueMatch
        fields = [
            'id', 'league', 'game_session', 'round_number', 'match_number',
            'participant1', 'participant2', 'winner', 'scheduled_time', 'status',
            'participant1_name', 'participant2_name', 'winner_name', 'league_title'
        ]
        read_only_fields = ['id', 'winner', 'status']
    
    def get_participant1_name(self, obj):
        return obj.participant1.display_name
    
    def get_participant2_name(self, obj):
        return obj.participant2.display_name
    
    def get_winner_name(self, obj):
        return obj.winner.display_name if obj.winner else None
    
    def get_league_title(self, obj):
        return obj.league.title