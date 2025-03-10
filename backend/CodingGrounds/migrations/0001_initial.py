# Generated by Django 5.1.5 on 2025-02-27 06:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.CharField(help_text='CSS class for the badge icon', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CodingProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('display_name', models.CharField(max_length=200)),
                ('rating', models.IntegerField(default=1500)),
                ('problems_solved', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('bio', models.TextField(blank=True)),
                ('avatar', models.CharField(blank=True, max_length=200)),
                ('streak', models.IntegerField(default=0, help_text='Consecutive days with submissions')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('badges', models.ManyToManyField(blank=True, to='CodingGrounds.badge')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coding_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='CodingProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('difficulty', models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], default=1)),
                ('test_cases', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('time_limit', models.FloatField(default=1.0, help_text='Time limit in seconds')),
                ('memory_limit', models.IntegerField(default=128, help_text='Memory limit in MB')),
                ('tags', models.JSONField(blank=True, default=list, help_text='List of tags for the problem')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_problems', to='CodingGrounds.codingprofile')),
            ],
            options={
                'ordering': ['difficulty', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='GameParticipation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_time', models.DateTimeField(auto_now_add=True)),
                ('problems_solved', models.IntegerField(default=0)),
                ('total_time', models.IntegerField(default=0, help_text='Total time in seconds')),
                ('final_rank', models.IntegerField(blank=True, null=True)),
                ('score', models.IntegerField(default=0)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_participations', to='CodingGrounds.codingprofile')),
            ],
            options={
                'ordering': ['-problems_solved', 'total_time'],
            },
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(default='Coding Competition', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('max_participants', models.IntegerField(default=0, help_text='0 for unlimited')),
                ('is_private', models.BooleanField(default=False)),
                ('access_code', models.CharField(blank=True, max_length=20, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_sessions', to='CodingGrounds.codingprofile')),
                ('participants', models.ManyToManyField(related_name='participating_sessions', through='CodingGrounds.GameParticipation', to='CodingGrounds.codingprofile')),
                ('problems', models.ManyToManyField(related_name='game_sessions', to='CodingGrounds.codingproblem')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.AddField(
            model_name='gameparticipation',
            name='game_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='CodingGrounds.gamesession'),
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('language', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('wrong_answer', 'Wrong Answer'), ('time_limit', 'Time Limit Exceeded'), ('memory_limit', 'Memory Limit Exceeded'), ('runtime_error', 'Runtime Error'), ('compilation_error', 'Compilation Error')], default='pending', max_length=20)),
                ('execution_time', models.FloatField(blank=True, null=True)),
                ('memory_usage', models.FloatField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('game_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submissions', to='CodingGrounds.gamesession')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='CodingGrounds.codingproblem')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='CodingGrounds.codingprofile')),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='codingprofile',
            index=models.Index(fields=['-rating'], name='CodingGroun_rating_3a29f0_idx'),
        ),
        migrations.AddIndex(
            model_name='codingprofile',
            index=models.Index(fields=['username'], name='CodingGroun_usernam_ffe44a_idx'),
        ),
        migrations.AddIndex(
            model_name='codingproblem',
            index=models.Index(fields=['difficulty'], name='CodingGroun_difficu_da46e6_idx'),
        ),
        migrations.AddIndex(
            model_name='codingproblem',
            index=models.Index(fields=['created_at'], name='CodingGroun_created_7c9886_idx'),
        ),
        migrations.AddIndex(
            model_name='gamesession',
            index=models.Index(fields=['-start_time'], name='CodingGroun_start_t_18d879_idx'),
        ),
        migrations.AddIndex(
            model_name='gamesession',
            index=models.Index(fields=['is_active'], name='CodingGroun_is_acti_fe7290_idx'),
        ),
        migrations.AddIndex(
            model_name='gameparticipation',
            index=models.Index(fields=['game_session', '-problems_solved', 'total_time'], name='CodingGroun_game_se_b13b97_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='gameparticipation',
            unique_together={('game_session', 'profile')},
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['-submitted_at'], name='CodingGroun_submitt_30961e_idx'),
        ),
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['profile', 'problem'], name='CodingGroun_profile_10d444_idx'),
        ),
    ]
