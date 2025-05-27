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
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.user.username

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
        return f"{self.profile.user.username}'s submission for {self.problem.title}"
    
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
    max_participants = models.IntegerField(default=2, help_text="0 for unlimited")
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

    def calculate_score(self, time_taken, difficulty, incorrect_submissions, total_submissions, player_rating, opponent_rating, previous_score):
        """Calculate score based on performance metrics"""
        # Base score depends on problem difficulty
        base_score = difficulty * 100
        
        # Time penalty (the faster, the better)
        time_factor = max(0, 1 - (time_taken / (15 * 60)))  # Normalize to 15 min max
        
        # Penalty for incorrect submissions
        accuracy = 1.0
        if total_submissions > 0:
            accuracy = max(0, 1 - (incorrect_submissions / total_submissions))
        
        # Calculate final score
        score = int(base_score * time_factor * accuracy)
        
        # Ensure minimum score
        return max(previous_score, score)

    def end_session(self):
        """End the game session and calculate final rankings and scores using duel logic"""
        self.is_active = False
        self.end_time = timezone.now()
        self.save()
        
        participations = list(self.participations.all())
        sorted_participations = sorted(
            participations, 
            key=lambda p: (p.problems_solved, -p.total_time),
            reverse=True
        )
        
        # Only for duels (2 participants)
        if len(sorted_participations) == 2:
            p1, p2 = sorted_participations
            # For each participant, gather duel parameters
            for i, participation in enumerate([p1, p2]):
                opponent = p2 if i == 0 else p1
                # Aggregate stats for the session
                # For simplicity, use the hardest problem's difficulty
                problems = self.problems.all()
                difficulty = max([prob.difficulty for prob in problems]) if problems else 1
                # Submissions for this participant in this session
                submissions = participation.profile.submissions.filter(game_session=self)
                total_submissions = submissions.count()
                incorrect_submissions = submissions.exclude(status=Submission.Status.ACCEPTED).count()
                time_taken = participation.total_time
                player_rating = participation.profile.rating
                opponent_rating = opponent.profile.rating
                previous_score = participation.score
                # Calculate new score
                new_score = self.calculate_score(
                    time_taken,
                    difficulty,
                    incorrect_submissions,
                    total_submissions,
                    player_rating,
                    opponent_rating,
                    previous_score
                )
                participation.final_rank = i + 1
                participation.score = new_score
                participation.save()
                
                # Update ELO rating
                self.update_elo_rating(participation, opponent)
        else:
            # For non-duel sessions
            for rank, participation in enumerate(sorted_participations, 1):
                participation.final_rank = rank
                participation.score = max(0, 100 - (rank - 1) * 10) * participation.problems_solved
                participation.save()
                
                # Update rating based on final ranking
                self.update_multi_player_rating(participation, sorted_participations)
    
    def update_elo_rating(self, player_participation, opponent_participation):
        """Update player's ELO rating using the standard ELO formula"""
        # Constants
        K_FACTOR = 32  # K-factor determines how much ratings change (higher = more volatile)
        
        # Get profiles and current ratings
        player = player_participation.profile
        opponent = opponent_participation.profile
        player_rating = player.rating
        opponent_rating = opponent.rating
        
        # Determine actual outcome (1 for win, 0.5 for draw, 0 for loss)
        outcome = 0.5  # Default to draw
        
        if player_participation.problems_solved > opponent_participation.problems_solved:
            outcome = 1.0  # Win
        elif player_participation.problems_solved < opponent_participation.problems_solved:
            outcome = 0.0  # Loss
        else:
            # If tied on problems, compare time
            if player_participation.total_time < opponent_participation.total_time:
                outcome = 1.0  # Win by time
            elif player_participation.total_time > opponent_participation.total_time:
                outcome = 0.0  # Loss by time
        
        # Calculate expected outcome using ELO formula
        expected = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
        
        # Calculate rating change
        rating_change = int(K_FACTOR * (outcome - expected))
        
        # Store the rating change in the participation record
        player_participation.rating_change = rating_change
        player_participation.save()
        
        # Update player rating
        player.rating = max(100, player.rating + rating_change)  # Ensure minimum rating of 100
        player.save()
        
        # Update rank if needed (based on new rating)
        # This could be improved with a periodic batch job to update all ranks
        CodingProfile.objects.filter(rating__lt=player.rating).update(rank=models.F('rank') + 1)
        
        # Return the rating change for reference
        return rating_change
    
    def update_multi_player_rating(self, participation, all_participations):
        """Update ratings for multi-player games using a modified ELO system"""
        # Constants
        K_FACTOR = 24  # Slightly lower K-factor for multiplayer
        
        player = participation.profile
        player_rank = participation.final_rank
        total_players = len(all_participations)
        
        # Skip if only one player
        if total_players <= 1:
            return 0
        
        # Calculate normalized rank from 0 to 1 (0 = best, 1 = worst)
        normalized_rank = (player_rank - 1) / (total_players - 1) if total_players > 1 else 0
        
        # Calculate average opponent rating
        avg_opponent_rating = sum(p.profile.rating for p in all_participations if p.profile.id != player.id) / (total_players - 1)
        
        # Expected performance based on rating difference
        rating_diff = avg_opponent_rating - player.rating
        expected_rank = 1 / (1 + 10 ** (rating_diff / 400))
        
        # Rating change based on expected vs actual performance
        # A player who performs as expected (normalized_rank ≈ expected_rank) gets minimal change
        # Outperform expectations = positive change, underperform = negative change
        rating_change = int(K_FACTOR * (expected_rank - normalized_rank))
        
        # Store the rating change in the participation record
        participation.rating_change = rating_change
        participation.save()
        
        # Update player rating
        player.rating = max(100, player.rating + rating_change)
        player.save()
        
        # Return the rating change
        return rating_change

    def _update_user_rating(self, participation):
        """Legacy method - kept for backward compatibility"""
        # This is now handled by update_elo_rating and update_multi_player_rating
        pass
    
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
    rating_change = models.IntegerField(default=0, help_text="Change in rating after the session")

    class Meta:
        unique_together = ('game_session', 'profile')
        ordering = ['-problems_solved', 'total_time']
        indexes = [
            models.Index(fields=['game_session', '-problems_solved', 'total_time']),
        ]
    
    def __str__(self):
        return f"{self.profile.user.username} in {self.game_session.title}"