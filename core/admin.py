from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Role', {'fields': ('role', 'specialization')}),
        ('Status', {'fields': ('is_active',)}),
    )


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_of_birth', 'age_calculated', 'parent', 'grade_level')
    list_filter = ('grade_level', 'gender', 'created_at')
    search_fields = ('first_name', 'last_name')
    readonly_fields = ('age_calculated',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('assessment_type', 'child', 'assessment_date', 'completed_by', 'is_complete')
    list_filter = ('assessment_type', 'is_complete', 'assessment_date')
    search_fields = ('child__first_name', 'child__last_name')


@admin.register(IEP)
class IEPAdmin(admin.ModelAdmin):
    list_display = ('child', 'status', 'iep_start_date', 'iep_review_date', 'is_ai_generated')
    list_filter = ('status', 'is_ai_generated', 'iep_start_date')
    search_fields = ('child__first_name', 'child__last_name')


@admin.register(IEPGoals)
class IEPGoalsAdmin(admin.ModelAdmin):
    list_display = ('goal_number', 'iep', 'status', 'target_completion_date')
    list_filter = ('status', 'goal_category')
    search_fields = ('goal_statement',)


@admin.register(WeeklyProgressReport)
class WeeklyProgressReportAdmin(admin.ModelAdmin):
    list_display = ('child', 'report_type', 'week_start_date', 'submitted_by')
    list_filter = ('report_type', 'report_date')
    search_fields = ('child__first_name', 'child__last_name')
    ordering = ('-report_date',)


# Register other models
admin.site.register(ChildrenEligibility)
admin.site.register(DevelopmentalHistory)
admin.site.register(AssessmentSkillArea)
admin.site.register(DisorderScreening)
admin.site.register(ParentInput)
admin.site.register(TeacherInput)
admin.site.register(SpecialistInput)
admin.site.register(ServicesAndTherapies)
admin.site.register(IEPPerformanceLevels)
admin.site.register(IEPObjectives)
admin.site.register(PlannedActivitiesServices)
admin.site.register(Accommodations)
admin.site.register(WeeklyServicesProvided)
admin.site.register(WeeklyGoalsProgress)
admin.site.register(WeeklyProgressSummary)
admin.site.register(ProgressReportAggregate)
admin.site.register(AuditLog)
admin.site.register(AIGenerationLog)
admin.site.register(AssessmentRequest)
