from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.utils import timezone

class Badge(models.Model):
    """Badges that can be earned by users"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="CSS class for the badge icon")
    
    def __str__(self):
        return self.name

class CodingProfile(models.Model):
    """Primary profile for coding platform users"""
    # This will be created first, then link to a User model
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='coding_profile',
        null=True,  # Allow null initially when profile is created before user
        blank=True
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=200)
    rating = models.IntegerField(default=1500)
    problems_solved = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=200, blank=True)
    streak = models.IntegerField(default=0, help_text="Consecutive days with submissions")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    badges = models.ManyToManyField(Badge, blank=True)
    
    class Meta:
        ordering = ['-rating']
        indexes = [
            models.Index(fields=['-rating']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.username
    
    def create_auth_user(self, password):
        """Create the associated auth User model"""
        if not self.user:
            user = User.objects.create_user(
                username=self.username,
                email=self.email,
                password=password
            )
            self.user = user
            self.save()
            return user
        return self.user

    def update_streak(self):
        """Update the user's streak based on submissions"""
        latest_submission = self.submissions.order_by('-submitted_at').first()
        if not latest_submission:
            return
            
        today = timezone.now().date()
        submission_date = latest_submission.submitted_at.date()
        
        if submission_date == today:
            # Already submitted today, nothing to do
            return
        elif submission_date == today - timedelta(days=1):
            # Submitted yesterday, increment streak
            self.streak += 1
        else:
            # Streak broken
            self.streak = 0
        self.save()

class CodingProblem(models.Model):
    """Coding problems that users can solve"""
    class Difficulty(models.IntegerChoices):
        EASY = 1, 'Easy'
        MEDIUM = 2, 'Medium'
        HARD = 3, 'Hard'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.IntegerField(
        choices=Difficulty.choices,
        default=Difficulty.EASY
    )
    test_cases = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CodingProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_problems'
    )
    time_limit = models.FloatField(default=1.0, help_text="Time limit in seconds")
    memory_limit = models.IntegerField(default=128, help_text="Memory limit in MB")
    tags = models.JSONField(default=list, blank=True, help_text="List of tags for the problem")
    
    class Meta:
        ordering = ['difficulty', 'created_at']
        indexes = [
            models.Index(fields=['difficulty']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

class Submission(models.Model):
    """Code submissions for solving problems"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        WRONG_ANSWER = 'wrong_answer', 'Wrong Answer'
        TIME_LIMIT_EXCEEDED = 'time_limit', 'Time Limit Exceeded'
        MEMORY_LIMIT_EXCEEDED = 'memory_limit', 'Memory Limit Exceeded'
        RUNTIME_ERROR = 'runtime_error', 'Runtime Error'
        COMPILATION_ERROR = 'compilation_error', 'Compilation Error'
    
    profile = models.ForeignKey(CodingProfile, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    execution_time = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    game_session = models.ForeignKey(
        'GameSession', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='submissions'
    )
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['-submitted_at']),
            models.Index(fields=['profile', 'problem']),
        ]

    def __str__(self):
        return f"{self.profile.username}'s submission for {self.problem.title}"
    
    def save(self, *args, **kwargs):
        # If this is a new successful submission
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.status == self.Status.ACCEPTED:
            # Check if this is the first time this user solved this problem
            previous_accepted = Submission.objects.filter(
                profile=self.profile,
                problem=self.problem,
                status=self.Status.ACCEPTED
            ).exclude(pk=self.pk).exists()
            
            if not previous_accepted:
                # Increment problems_solved count
                self.profile.problems_solved += 1
                self.profile.save()
                
                # Update game participation if part of a session
                if self.game_session:
                    participation = GameParticipation.objects.get(
                        game_session=self.game_session,
                        profile=self.profile
                    )
                    participation.problems_solved += 1
                    
                    # Calculate time since session start
                    time_delta = self.submitted_at - self.game_session.start_time
                    seconds = int(time_delta.total_seconds())
                    
                    # Add to total time (used for tie-breaking)
                    participation.total_time += seconds
                    participation.save()

class GameSession(models.Model):
    """Competitive coding sessions with multiple participants"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="Coding Competition")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    problems = models.ManyToManyField(CodingProblem, related_name='game_sessions')
    participants = models.ManyToManyField(
        CodingProfile, 
        through='GameParticipation',
        related_name='participating_sessions'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CodingProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_sessions'
    )
    max_participants = models.IntegerField(default=0, help_text="0 for unlimited")
    is_private = models.BooleanField(default=False)
    access_code = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['-start_time']),
            models.Index(fields=['is_active']),
        ]

    def add_participant(self, profile):
        """Add a user profile to the game session and create GameParticipation"""
        if not self.participants.filter(id=profile.id).exists():
            GameParticipation.objects.create(game_session=self, profile=profile)
            return True
        return False

    def remove_participant(self, profile):
        """Remove a user profile from the game session"""
        self.participants.remove(profile)
    
    def all_participants_ready(self):
        """Check if all participants are ready to start the competition"""
        return not self.participations.filter(is_ready=False).exists()

    def start_if_ready(self):
        """Start the session if all participants are ready"""
        if self.all_participants_ready() and self.is_active and not self.start_time:
            self.start_time = timezone.now()
            self.end_time = self.start_time + timedelta(minutes=15)  # or your default duration
            self.save()
            return True
        return False

    def end_session(self):
        """End the game session and calculate final rankings"""
        self.is_active = False
        self.end_time = timezone.now()
        self.save()
        
        # Calculate and update participant rankings
        participations = self.participations.all()
        sorted_participations = sorted(
            participations, 
            key=lambda p: (p.problems_solved, -p.total_time),
            reverse=True
        )
        
        for rank, participation in enumerate(sorted_participations, 1):
            participation.final_rank = rank
            # Calculate score based on rank and problems solved
            participation.score = max(0, 100 - (rank - 1) * 10) * participation.problems_solved
            participation.save()
            
            # Update user ratings based on performance
            self._update_user_rating(participation)

    def _update_user_rating(self, participation):
        """Update a user's rating based on their performance in this session"""
        # Simple ELO-like rating adjustment
        profile = participation.profile
        expected_rank = self._get_expected_rank(profile)
        actual_rank = participation.final_rank
        
        # Calculate rating change based on expected vs actual performance
        # Higher ranks (lower numbers) are better
        rank_diff = expected_rank - actual_rank
        rating_change = int(rank_diff * 10)
        
        # Apply rating change with some constraints
        profile.rating = max(0, profile.rating + rating_change)
        profile.save()
    
    def _get_expected_rank(self, profile):
        """Calculate expected rank based on current rating"""
        participants = self.participants.all()
        ratings = [p.rating for p in participants]
        ratings.sort(reverse=True)
        
        try:
            expected_rank = ratings.index(profile.rating) + 1
        except ValueError:
            # If rating not found, estimate position
            for i, rating in enumerate(ratings, 1):
                if profile.rating >= rating:
                    return i
            return len(ratings) + 1
            
        return expected_rank

    def __str__(self):
        return f"{self.title} - {self.start_time}"
    
    def save(self, *args, **kwargs):
        if not self.end_time and self.start_time:
            self.end_time = self.start_time + timedelta(minutes=15)
        super().save(*args, **kwargs)

class GameParticipation(models.Model):
    """Junction table between GameSession and CodingProfile with additional data"""
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='participations')
    profile = models.ForeignKey(CodingProfile, on_delete=models.CASCADE, related_name='game_participations')
    join_time = models.DateTimeField(auto_now_add=True)
    problems_solved = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0, help_text="Total time in seconds")
    final_rank = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(default=0)
    is_ready = models.BooleanField(default=False)

    class Meta:
        unique_together = ('game_session', 'profile')
        ordering = ['-problems_solved', 'total_time']
        indexes = [
            models.Index(fields=['game_session', '-problems_solved', 'total_time']),
        ]
    
    def __str__(self):
        return f"{self.profile.username} in {self.game_session.title}"