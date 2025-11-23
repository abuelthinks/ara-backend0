from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet, ChildViewSet, ChildrenEligibilityViewSet,
    DevelopmentalHistoryViewSet, AssessmentViewSet,
    AssessmentSkillAreaViewSet, DisorderScreeningViewSet,
    ParentInputViewSet, TeacherInputViewSet, SpecialistInputViewSet,
    ServicesAndTherapiesViewSet, IEPViewSet, IEPGoalsViewSet,
    IEPPerformanceLevelsViewSet, AccommodationsViewSet,
    WeeklyProgressReportViewSet, ProgressReportAggregateViewSet,
    AuditLogViewSet, AIGenerationLogViewSet
)

router = DefaultRouter()

# User management
router.register(r'users', UserViewSet, basename='user')

# Child management
router.register(r'children', ChildViewSet, basename='child')
router.register(r'children-eligibilities', ChildrenEligibilityViewSet, basename='children-eligibility')
router.register(r'developmental-histories', DevelopmentalHistoryViewSet, basename='developmental-history')

# Assessment management
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'assessment-skill-areas', AssessmentSkillAreaViewSet, basename='assessment-skill-area')
router.register(r'disorder-screenings', DisorderScreeningViewSet, basename='disorder-screening')

# Input management (Parent, Teacher, Specialist)
router.register(r'parent-inputs', ParentInputViewSet, basename='parent-input')
router.register(r'teacher-inputs', TeacherInputViewSet, basename='teacher-input')
router.register(r'specialist-inputs', SpecialistInputViewSet, basename='specialist-input')

# Services and Therapies
router.register(r'services', ServicesAndTherapiesViewSet, basename='service')

# IEP management
router.register(r'ieps', IEPViewSet, basename='iep')
router.register(r'iep-goals', IEPGoalsViewSet, basename='iep-goal')
router.register(r'iep-performance-levels', IEPPerformanceLevelsViewSet, basename='iep-performance-level')
router.register(r'accommodations', AccommodationsViewSet, basename='accommodation')

# Progress reports
router.register(r'weekly-progress-reports', WeeklyProgressReportViewSet, basename='weekly-progress-report')
router.register(r'progress-report-aggregates', ProgressReportAggregateViewSet, basename='progress-report-aggregate')

# Audit and logging
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'ai-generation-logs', AIGenerationLogViewSet, basename='ai-generation-log')

urlpatterns = [
    path('', include(router.urls)),
]
