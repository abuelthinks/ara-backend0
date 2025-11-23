from rest_framework import serializers
from core.models import (
    User, Child, ChildrenEligibility, DevelopmentalHistory,
    Assessment, AssessmentSkillArea, DisorderScreening,
    ParentInput, TeacherInput, SpecialistInput,
    ServicesAndTherapies, IEP, IEPPerformanceLevels,
    IEPGoals, IEPObjectives, PlannedActivitiesServices,
    Accommodations, WeeklyProgressReport, WeeklyServicesProvided,
    WeeklyGoalsProgress, WeeklyProgressSummary, ProgressReportAggregate,
    AuditLog, AIGenerationLog
)


# ==================== USER SERIALIZERS ====================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'username', 'first_name', 'last_name',
            'role', 'phone', 'specialization', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone', 'specialization'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ==================== CHILD & ELIGIBILITY SERIALIZERS ====================
class ChildrenEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenEligibility
        fields = [
            'eligibility_id', 'child', 'eligibility_type', 'eligibility_other',
            'date_identified', 'diagnostic_report_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['eligibility_id', 'created_at', 'updated_at']


class DevelopmentalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelopmentalHistory
        fields = [
            'history_id', 'child', 'sat_up_age', 'crawled_age', 'walked_age',
            'first_words_age', 'formed_sentences_age', 'previous_school_name',
            'previous_school_level', 'prior_special_ed_services', 'prior_services_description',
            'prior_iep_existed', 'other_prior_services', 'created_at', 'updated_at'
        ]
        read_only_fields = ['history_id', 'created_at', 'updated_at']


class ChildSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    secondary_parent_name = serializers.CharField(source='secondary_parent.get_full_name', read_only=True, allow_null=True)
    eligibilities = ChildrenEligibilitySerializer(many=True, read_only=True)
    developmental_history = DevelopmentalHistorySerializer(read_only=True)
    
    class Meta:
        model = Child
        fields = [
            'child_id', 'first_name', 'last_name', 'date_of_birth', 'age',
            'gender', 'primary_language', 'grade_level', 'medical_alerts',
            'medications', 'parent', 'parent_name', 'secondary_parent',
            'secondary_parent_name', 'eligibilities', 'developmental_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['child_id', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        return obj.age_calculated


# ==================== ASSESSMENT SERIALIZERS ====================
class AssessmentSkillAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSkillArea
        fields = [
            'skill_area_id', 'assessment', 'category', 'skill_name',
            'rating', 'comments', 'created_at'
        ]
        read_only_fields = ['skill_area_id', 'created_at']


class DisorderScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisorderScreening
        fields = [
            'screening_id', 'assessment', 'disorder_type', 'screening_items',
            'risk_level', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['screening_id', 'created_at', 'updated_at']


class AssessmentSerializer(serializers.ModelSerializer):
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    skill_areas = AssessmentSkillAreaSerializer(many=True, read_only=True)
    disorder_screenings = DisorderScreeningSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'assessment_id', 'child', 'assessment_type', 'assessment_date',
            'completed_by', 'completed_by_name', 'is_complete', 'skill_areas',
            'disorder_screenings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assessment_id', 'created_at', 'updated_at']


# ==================== INPUT SERIALIZERS ====================
class ParentInputSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    
    class Meta:
        model = ParentInput
        fields = [
            # Primary/Relationship Fields
            'parent_input_id', 'child', 'child_name', 'parent', 'parent_name',
            'submission_date', 'created_at', 'updated_at',
            
            # SECTION A: Background Information
            'first_name', 'last_name', 'date_of_birth', 'gender', 'grade_level', 'primary_language',
            'iep_start_date', 'parent_guardian_name', 'parent_phone', 'parent_email',
            'diagnostic_report_url', 'medical_alerts', 'medications',
            'eligibility_criteria',
            
            # SECTION B: Developmental History and Assessment
            'sat_up_age', 'crawled_age', 'walked_age', 'first_words_age', 'formed_sentences_age',
            'previous_school_name', 'special_education_services_received', 'has_prior_iep', 'other_prior_services',
            'areas_of_concern',
            
            # SECTION C: Parent/Guardian Input
            'primary_concerns', 'goals_for_child', 'strategies_approaches_that_work',
            
            # SECTION D: Behavioral Information
            'behavioral_difficulties', 'behavior_description_home_social', 'behavior_frustration_triggers',
            'triggers_examples', 'calming_strategies_work',
            'communication_style', 'communication_other', 'primary_communication_method',
            'peer_interaction_level', 'peer_adult_interaction', 'comfort_environment',
            
            # SECTION E: Sensory and Physical Needs
            'sensory_sensitivities', 'sensory_sensitivity_other',
            'physical_accommodations_needed', 'physical_accommodations_required', 'physical_accommodations_details',
            
            # SECTION F: Goals and Expectations
            'goals_timeframe', 'goals_this_year', 'goals_3_5_years',
            
            # SECTION G: Home Environment
            'strategies_routines_home', 'additional_support_needs', 'additional_support_resources_needed',
        ]
        read_only_fields = [
            'parent_input_id', 'submission_date', 
            'created_at', 'updated_at', 'parent_name', 'child_name'
        ]


class TeacherInputSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    
    class Meta:
        model = TeacherInput
        fields = [
            'teacher_input_id', 'child', 'child_name', 'teacher', 'teacher_name',
            'submission_date', 'grade_level', 'sessions_attended',
            'prewriting_progress', 'prewriting_notes', 'english_progress', 'english_notes',
            'math_progress', 'math_notes', 'science_progress', 'science_notes',
            'arts_fine_motor_progress', 'arts_fine_motor_notes',
            'classroom_behavior_progress', 'classroom_behavior_notes',
            'overall_comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['teacher_input_id', 'submission_date', 'created_at', 'updated_at']


class SpecialistInputSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(source='specialist.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    
    class Meta:
        model = SpecialistInput
        fields = [
            'specialist_input_id', 'child', 'child_name', 'specialist', 'specialist_name',
            'submission_date', 'specialist_type', 'areas_of_concern', 'strengths_identified',
            'disorder_screening_results', 'additional_information', 'created_at', 'updated_at'
        ]
        read_only_fields = ['specialist_input_id', 'submission_date', 'created_at', 'updated_at']


# ==================== SERVICES SERIALIZERS ====================
class ServicesAndTherapiesSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    
    class Meta:
        model = ServicesAndTherapies
        fields = [
            'service_id', 'child', 'child_name', 'service_type', 'service_other_description',
            'therapist', 'therapist_name', 'frequency', 'frequency_days_per_week',
            'goal_description', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['service_id', 'created_at', 'updated_at']


# ==================== IEP SERIALIZERS ====================
class IEPPerformanceLevelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IEPPerformanceLevels
        fields = [
            'performance_id', 'iep', 'skill_category', 'skill_name',
            'current_level', 'level_description', 'assessment_source', 'created_at'
        ]
        read_only_fields = ['performance_id', 'created_at']


class IEPObjectivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IEPObjectives
        fields = [
            'objective_id', 'goal', 'objective_number', 'objective_statement',
            'success_criteria', 'target_date', 'progress_tracking_method',
            'status', 'created_at'
        ]
        read_only_fields = ['objective_id', 'created_at']


class PlannedActivitiesServicesSerializer(serializers.ModelSerializer):
    responsible_person_name = serializers.CharField(source='responsible_personnel.get_full_name', read_only=True)
    
    class Meta:
        model = PlannedActivitiesServices
        fields = [
            'activity_id', 'goal', 'activity_description', 'activity_type',
            'frequency', 'duration', 'setting', 'responsible_personnel',
            'responsible_person_name', 'start_date', 'end_date', 'created_at'
        ]
        read_only_fields = ['activity_id', 'created_at']


class AccommodationsSerializer(serializers.ModelSerializer):
    responsible_person_name = serializers.CharField(source='responsible_person.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Accommodations
        fields = [
            'accommodation_id', 'iep', 'accommodation_type', 'accommodation_description',
            'category', 'implementation_location', 'responsible_person',
            'responsible_person_name', 'implementation_start_date', 'notes', 'created_at'
        ]
        read_only_fields = ['accommodation_id', 'created_at']


class IEPGoalsSerializer(serializers.ModelSerializer):
    objective_details = IEPObjectivesSerializer(many=True, read_only=True)
    planned_activities = PlannedActivitiesServicesSerializer(many=True, read_only=True)
    
    class Meta:
        model = IEPGoals
        fields = [
            'goal_id', 'iep', 'goal_number', 'goal_statement', 'goal_category',
            'objectives', 'timeframe_months', 'target_completion_date',
            'measurement_method', 'responsible_personnel', 'status',
            'objective_details', 'planned_activities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['goal_id', 'created_at', 'updated_at']


class IEPSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    goals = IEPGoalsSerializer(many=True, read_only=True)
    performance_levels = IEPPerformanceLevelsSerializer(many=True, read_only=True)
    accommodations = AccommodationsSerializer(many=True, read_only=True)
    
    class Meta:
        model = IEP
        fields = [
            'iep_id', 'child', 'child_name', 'iep_start_date', 'iep_review_date',
            'created_by', 'created_by_name', 'is_ai_generated', 'ai_generated_date',
            'status', 'goals', 'performance_levels', 'accommodations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['iep_id', 'created_at', 'updated_at']


# ==================== WEEKLY PROGRESS REPORT SERIALIZERS ====================
class WeeklyServicesProvidedSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyServicesProvided
        fields = [
            'service_record_id', 'report', 'service_type', 'service_other_description',
            'session_count', 'notes'
        ]
        read_only_fields = ['service_record_id']


class WeeklyGoalsProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyGoalsProgress
        fields = [
            'weekly_goal_progress_id', 'report', 'iep_goal', 'goal_statement',
            'objective_statement', 'weekly_progress_description', 'progress_percentage',
            'progress_status', 'created_at'
        ]
        read_only_fields = ['weekly_goal_progress_id', 'created_at']


class WeeklyProgressSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyProgressSummary
        fields = [
            'summary_id', 'report', 'strengths_observed', 'areas_for_improvement',
            'recommendations_next_week', 'therapist_comments', 'teacher_comments', 'created_at'
        ]
        read_only_fields = ['summary_id', 'created_at']


class WeeklyProgressReportSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    services_provided = WeeklyServicesProvidedSerializer(many=True, read_only=True)
    goal_progress = WeeklyGoalsProgressSerializer(many=True, read_only=True)
    summary = WeeklyProgressSummarySerializer(read_only=True)
    
    class Meta:
        model = WeeklyProgressReport
        fields = [
            'report_id', 'child', 'child_name', 'report_type', 'submitted_by',
            'submitted_by_name', 'report_date', 'week_start_date', 'week_end_date',
            'age', 'grade_level', 'sessions_attended', 'special_needs_type',
            'services_provided', 'goal_progress', 'summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at']


class ProgressReportAggregateSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.first_name', read_only=True)
    
    class Meta:
        model = ProgressReportAggregate
        fields = [
            'aggregate_id', 'child', 'child_name', 'iep', 'report_period_start_date',
            'report_period_end_date', 'weeks_included', 'overall_progress_summary',
            'goals_progress_status', 'adjustments_recommended', 'generated_at'
        ]
        read_only_fields = ['aggregate_id', 'generated_at']


# ==================== AUDIT & LOGGING SERIALIZERS ====================
class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'log_id', 'user', 'user_name', 'action_type', 'table_name',
            'record_id', 'old_value', 'new_value', 'timestamp', 'ip_address',
            'compliance_notes'
        ]
        read_only_fields = ['log_id', 'timestamp']


class AIGenerationLogSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = AIGenerationLog
        fields = [
            'ai_log_id', 'generation_type', 'source_data_id', 'generated_content_id',
            'ai_model_version', 'confidence_score', 'human_review_status',
            'reviewer', 'reviewer_name', 'generated_at'
        ]
        read_only_fields = ['ai_log_id', 'generated_at']
