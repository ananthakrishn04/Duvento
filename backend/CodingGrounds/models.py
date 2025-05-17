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
        return f"{self.profile.user.username} in {self.game_session.title}"


class League(models.Model):
    """A tournament with multiple game sessions leading to finals"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=8, help_text="Must be a power of 2 (e.g. 4, 8, 16)")
    
    # League creator
    created_by = models.ForeignKey(
        CodingProfile, 
        on_delete=models.CASCADE, 
        related_name='created_leagues'
    )
    
    # League participants
    participants = models.ManyToManyField(
        CodingProfile, 
        through='LeagueParticipation',
        related_name='participating_leagues'
    )
    
    # Problems to be used in the league sessions
    problems = models.ManyToManyField(
        CodingProblem, 
        related_name='league_problems',
        blank=True
    )
    
    # Access control
    is_private = models.BooleanField(default=False)
    access_code = models.CharField(max_length=20, blank=True, null=True)
    
    # League status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('registration', 'Registration Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='registration'
    )
    
    # League format
    FORMAT_CHOICES = [
        ('knockout', 'Single Elimination'),
        ('double_elim', 'Double Elimination'),
        ('round_robin', 'Round Robin')
    ]
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='knockout'
    )
    
    # League settings
    session_duration = models.IntegerField(default=15, help_text="Duration in minutes for each match")
    current_round = models.IntegerField(default=1)
    total_rounds = models.IntegerField(default=3)  # Calculated based on participants
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def add_participant(self, profile):
        """Add a participant to the league"""
        if self.status != 'registration':
            return False, "Registration is closed"
            
        if self.participants.count() >= self.max_participants:
            return False, "League is full"
            
        if self.participants.filter(id=profile.id).exists():
            return False, "Already registered"
            
        LeagueParticipation.objects.create(
            league=self,
            profile=profile
        )
        return True, "Successfully registered"
    
    def remove_participant(self, profile):
        """Remove a participant from the league"""
        if self.status != 'registration':
            return False, "Cannot remove participants after registration is closed"
            
        participation = LeagueParticipation.objects.filter(
            league=self,
            profile=profile
        ).first()
        
        if participation:
            participation.delete()
            return True, "Participant removed"
        return False, "Participant not found"
    
    def start_league(self):
        """Start the league and create the first round of sessions"""
        if self.status != 'registration':
            return False, "League is not in registration phase"
            
        participants_count = self.participants.count()
        if participants_count < 2:
            return False, "Need at least 2 participants"
        
        # Calculate total rounds needed based on participants
        # For knockout: log2(participants)
        self.total_rounds = max(1, (participants_count - 1).bit_length())
        
        # Set status to in progress
        self.status = 'in_progress'
        self.start_date = timezone.now()
        self.save()
        
        # Create first round matchups
        self._create_round_matchups(1)
        
        return True, "League started successfully"
    
    def _create_round_matchups(self, round_number):
        """Create game sessions for a specific round"""
        if round_number > self.total_rounds:
            self._finalize_league()
            return
            
        # Get participants for this round
        if round_number == 1:
            # First round: all participants
            participants = list(self.participants.all())
            
            # Seed/shuffle participants if needed
            # In a real app, you might want to seed based on rating
            import random
            random.shuffle(participants)
        else:
            # Later rounds: winners from previous round
            previous_matches = LeagueMatch.objects.filter(
                league=self,
                round_number=round_number-1
            )
            participants = []
            for match in previous_matches:
                if match.winner:
                    participants.append(match.winner)
        
        # Number of matches in this round
        num_matches = len(participants) // 2
        
        # Create matches
        for i in range(num_matches):
            participant1 = participants[i*2]
            participant2 = participants[i*2+1]
            
            # Create a game session for this match
            session = GameSession.objects.create(
                title=f"{self.title} - Round {round_number}, Match {i+1}",
                description=f"League match between {participant1.display_name} and {participant2.display_name}",
                max_participants=2,  # Just the two participants
                is_private=True,  # Only for these participants
                created_by=self.created_by  # Creator is the league creator
            )
            
            # Add the participants
            session.add_participant(participant1)
            session.add_participant(participant2)
            
            # Add problems from the league
            league_problems = self.problems.all()
            if league_problems.exists():
                for problem in league_problems:
                    session.problems.add(problem)
            
            # Create league match record
            LeagueMatch.objects.create(
                league=self,
                game_session=session,
                round_number=round_number,
                participant1=participant1,
                participant2=participant2
            )
    
    def advance_round(self):
        """Advance to the next round of the league"""
        if self.status != 'in_progress':
            return False, "League is not in progress"
            
        # Check if current round is completed
        incomplete_matches = LeagueMatch.objects.filter(
            league=self,
            round_number=self.current_round,
            winner__isnull=True
        ).exists()
        
        if incomplete_matches:
            return False, "Current round is not complete"
            
        # Advance to next round
        self.current_round += 1
        self.save()
        
        if self.current_round > self.total_rounds:
            self._finalize_league()
            return True, "League completed"
            
        # Create next round matchups
        self._create_round_matchups(self.current_round)
        
        return True, "Advanced to next round"
    
    def _finalize_league(self):
        """Finalize the league and assign final rankings"""
        if self.format == 'knockout':
            # Find the winner (winner of the last match)
            final_match = LeagueMatch.objects.filter(
                league=self,
                round_number=self.total_rounds
            ).first()
            
            if final_match and final_match.winner:
                # Rank 1: Winner
                winner_participation = LeagueParticipation.objects.get(
                    league=self,
                    profile=final_match.winner
                )
                winner_participation.final_rank = 1
                winner_participation.save()
                
                # Rank 2: Runner-up (loser of the final match)
                runner_up = final_match.participant1 if final_match.winner == final_match.participant2 else final_match.participant2
                runner_up_participation = LeagueParticipation.objects.get(
                    league=self,
                    profile=runner_up
                )
                runner_up_participation.final_rank = 2
                runner_up_participation.save()
                
                # Semifinalists (lose in the semifinal round)
                if self.total_rounds > 1:
                    semifinal_matches = LeagueMatch.objects.filter(
                        league=self,
                        round_number=self.total_rounds - 1
                    )
                    
                    semifinalists = []
                    for match in semifinal_matches:
                        loser = match.participant1 if match.winner == match.participant2 else match.participant2
                        semifinalists.append(loser)
                    
                    # Both semifinalists get rank 3
                    for i, semifinalist in enumerate(semifinalists):
                        semifinalist_participation = LeagueParticipation.objects.get(
                            league=self,
                            profile=semifinalist
                        )
                        semifinalist_participation.final_rank = 3
                        semifinalist_participation.save()
                
                # Other participants: ranked based on the round they were eliminated
                for round_num in range(1, self.total_rounds):
                    matches = LeagueMatch.objects.filter(
                        league=self,
                        round_number=round_num
                    )
                    
                    eliminated_rank = 2**(self.total_rounds - round_num) + 1
                    
                    for match in matches:
                        if match.winner:
                            loser = match.participant1 if match.winner == match.participant2 else match.participant2
                            loser_participation = LeagueParticipation.objects.get(
                                league=self,
                                profile=loser
                            )
                            
                            if loser_participation.final_rank is None:
                                loser_participation.final_rank = eliminated_rank
                                loser_participation.save()
        
        # Update league status
        self.status = 'completed'
        self.end_date = timezone.now()
        self.save()
        
        # Update participant ratings based on final ranks
        self._update_participant_ratings()
    
    def _update_participant_ratings(self):
        """Update participant ratings based on league performance"""
        # Calculate average rating of participants
        participations = LeagueParticipation.objects.filter(league=self)
        
        if not participations.exists():
            return
            
        ratings = [p.profile.rating for p in participations]
        avg_rating = sum(ratings) / len(ratings)
        
        # Update ratings based on final rank
        for participation in participations:
            if participation.final_rank:
                # Higher rank (lower number) is better
                expected_rank = (len(participations) + 1) / 2  # Middle rank
                actual_rank = participation.final_rank
                
                # Calculate rating change
                rank_diff = expected_rank - actual_rank
                rating_change = int(rank_diff * 10)
                
                # Apply a scaling factor based on league size
                scaling = min(2.0, len(participations) / 8)
                rating_change = int(rating_change * scaling)
                
                # Apply rating change
                participation.profile.rating = max(0, participation.profile.rating + rating_change)
                participation.profile.save()

class LeagueParticipation(models.Model):
    """Junction table between League and CodingProfile with additional data"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='participations')
    profile = models.ForeignKey(CodingProfile, on_delete=models.CASCADE, related_name='league_participations')
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    final_rank = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(default=0)
    
    # Access control fields
    is_admin = models.BooleanField(default=False, help_text="Can edit league settings")
    
    class Meta:
        unique_together = ('league', 'profile')
        indexes = [
            models.Index(fields=['league', '-score']),
            models.Index(fields=['league', 'final_rank']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} in {self.league.title}"

class LeagueMatch(models.Model):
    """A match within a league"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matches')
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='league_match')
    round_number = models.IntegerField(default=1)
    match_number = models.IntegerField(default=1)
    
    # The two participants in this match
    participant1 = models.ForeignKey(
        CodingProfile, 
        on_delete=models.CASCADE, 
        related_name='league_matches_as_participant1'
    )
    participant2 = models.ForeignKey(
        CodingProfile, 
        on_delete=models.CASCADE, 
        related_name='league_matches_as_participant2'
    )
    
    # Winner of the match (null if not yet determined)
    winner = models.ForeignKey(
        CodingProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='league_matches_won'
    )
    
    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['league', 'round_number', 'match_number']
        indexes = [
            models.Index(fields=['league', 'round_number']),
        ]
        
    def __str__(self):
        return f"{self.league.title} - Round {self.round_number}, Match {self.match_number}"
    
    def determine_winner(self):
        """Determine the winner based on game session results"""
        if not self.game_session or self.game_session.is_active:
            return None
            
        # Get the participations in this game session
        p1_participation = GameParticipation.objects.filter(
            game_session=self.game_session,
            profile=self.participant1
        ).first()
        
        p2_participation = GameParticipation.objects.filter(
            game_session=self.game_session,
            profile=self.participant2
        ).first()
        
        if not p1_participation or not p2_participation:
            return None
            
        # Compare problems solved
        if p1_participation.problems_solved > p2_participation.problems_solved:
            self.winner = self.participant1
        elif p2_participation.problems_solved > p1_participation.problems_solved:
            self.winner = self.participant2
        else:
            # Tie-breaker: less time
            if p1_participation.total_time < p2_participation.total_time:
                self.winner = self.participant1
            else:
                self.winner = self.participant2
        
        self.status = 'completed'
        self.save()
        
        return self.winner