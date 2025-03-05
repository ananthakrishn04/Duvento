from django.contrib import admin
from .models import GameSession, Submission, CodingProfile, CodingProblem, GameParticipation

# Register your models here.
class SessionAdmin(admin.ModelAdmin):
    list_display = ["start_time","is_active","access_code"]

class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ["title","difficulty","created_at","created_by"]

class CodingProfileAdmin(admin.ModelAdmin):
    list_display = ["display_name","rating"]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["get_display_name","problem", "status", "language", "submitted_at"]
    list_filter = ["status", "language", "submitted_at"]
    search_fields = ["profile__username", "profile__display_name", "problem__title"]
    
    def get_display_name(self, obj):
        return obj.profile.display_name
    
    get_display_name.short_description = 'name'  # Sets column header in admin
    get_display_name.admin_order_field = 'profile__display_name'  # Allows sorting

class GameParticipationAdmin(admin.ModelAdmin):
    list_display = ["get_session_title","get_display_name","is_ready"]

    def get_session_title(self,obj):
        return obj.game_session.title

    def get_display_name(self, obj):
        return obj.profile.display_name

admin.site.register(GameSession,SessionAdmin)
admin.site.register(Submission,SubmissionAdmin)
admin.site.register(CodingProblem,CodingProblemAdmin)
admin.site.register(CodingProfile,CodingProfileAdmin)
admin.site.register(GameParticipation,GameParticipationAdmin)


