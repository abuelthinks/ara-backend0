from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# ==================== USER MODEL ====================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('TEACHER', 'Teacher'),
        ('SPECIALIST', 'Specialist'),
        ('PARENT', 'Parent/Guardian'),
    ]
    
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True, 
                                      help_text="For specialists: Speech Therapy, Occupational Therapy, etc.")
    is_active = models.BooleanField(default=True)  # Soft delete flag
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',  # Changed from default 'user_set'
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions_set',  # Changed from default 'user_set'
        blank=True,
        help_text='Specific permissions for this user.'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


# ==================== CHILDREN MODEL ====================
class Child(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('PREFER_NOT_TO_SAY', 'Prefer not to say'),
    ]
    
    child_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    date_of_birth = models.DateField(null=False)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    primary_language = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    medical_alerts = models.TextField(blank=True, help_text="Encrypted at rest - important medical information")
    medications = models.TextField(blank=True, help_text="Encrypted at rest - current medications")
    
    # Foreign keys to parents/guardians
    parent = models.ForeignKey(User, on_delete=models.PROTECT, 
                               related_name='children_as_primary_parent',
                               limit_choices_to={'role': 'PARENT'})
    secondary_parent = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                         null=True, blank=True,
                                         related_name='children_as_secondary_parent',
                                         limit_choices_to={'role': 'PARENT'})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['date_of_birth']),
        ]
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age_calculated(self):
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


# ==================== CHILDREN ELIGIBILITY ====================
class ChildrenEligibility(models.Model):
    ELIGIBILITY_TYPES = [
        ('AUTISM_SPECTRUM_DISORDER', 'Autism Spectrum Disorder'),
        ('ADHD_ADD', 'ADHD/ADD'),
        ('LEARNING_DISABILITY', 'Learning Disability'),
        ('SPEECH_LANGUAGE_IMPAIRMENT', 'Speech/Language Impairment'),
        ('DEVELOPMENTAL_DELAY', 'Developmental Delay'),
        ('OTHER', 'Other'),
    ]
    
    eligibility_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='eligibilities')
    eligibility_type = models.CharField(max_length=50, choices=ELIGIBILITY_TYPES, null=False)
    eligibility_other = models.CharField(max_length=200, blank=True)
    date_identified = models.DateField(null=False)
    diagnostic_report_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Children Eligibilities"
        indexes = [models.Index(fields=['child'])]
    
    def __str__(self):
        return f"{self.child} - {self.get_eligibility_type_display()}"


# ==================== DEVELOPMENTAL HISTORY ====================
class DevelopmentalHistory(models.Model):
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='developmental_history')
    
    # Developmental milestones (in months)
    sat_up_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    crawled_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    walked_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    first_words_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    formed_sentences_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # Previous school information
    previous_school_name = models.CharField(max_length=200, blank=True)
    previous_school_level = models.CharField(max_length=100, blank=True)
    
    # Prior services
    prior_special_ed_services = models.BooleanField(default=False)
    prior_services_description = models.TextField(blank=True)
    prior_iep_existed = models.BooleanField(default=False)
    other_prior_services = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Developmental History for {self.child}"


# ==================== ASSESSMENTS ====================
class Assessment(models.Model):
    assessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=50, default='LD-001')
    assessment_date = models.DateField(null=False)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                     related_name='completed_assessments')
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['assessment_date']),
        ]
    
    def __str__(self):
        return f"{self.assessment_type} - {self.child} ({self.assessment_date})"


# ==================== ASSESSMENT SKILL AREAS ====================
class AssessmentSkillArea(models.Model):
    CATEGORY_CHOICES = [
        ('ACADEMIC_SKILLS', 'Academic Skills'),
        ('COMMUNICATION_SKILLS', 'Communication Skills'),
        ('MOTOR_SKILLS', 'Motor Skills'),
        ('BEHAVIORAL_EMOTIONAL', 'Behavioral/Emotional'),
    ]
    
    RATING_CHOICES = [
        ('POOR', 'Poor'),
        ('FAIR', 'Fair'),
        ('GOOD', 'Good'),
        ('EXCELLENT', 'Excellent'),
    ]
    
    skill_area_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='skill_areas')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=False)
    skill_name = models.CharField(max_length=100, null=False)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=False)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['assessment'])]
    
    def __str__(self):
        return f"{self.skill_name} - {self.get_rating_display()}"


# ==================== DISORDER SCREENING ====================
class DisorderScreening(models.Model):
    DISORDER_TYPES = [
        ('ADHD', 'ADHD'),
        ('AUTISM_SPECTRUM_DISORDER', 'Autism Spectrum Disorder'),
        ('DYSLEXIA', 'Dyslexia'),
        ('DELAYED_SPEECH', 'Delayed Speech'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    screening_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='disorder_screenings')
    disorder_type = models.CharField(max_length=50, choices=DISORDER_TYPES, null=False)
    screening_items = models.JSONField(default=dict, blank=True)  # Array of screening checklist items
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [models.Index(fields=['assessment'])]
    
    def __str__(self):
        return f"{self.get_disorder_type_display()} - Risk: {self.risk_level}"


# ==================== INPUT MODELS ====================
class ParentInput(models.Model):
    COMMUNICATION_STYLES = [
        ('VERBAL', 'Verbal'),
        ('NON_VERBAL', 'Non-Verbal'),
        ('MIXED', 'Mixed'),
        ('OTHER', 'Other'),
    ]
    
    ENVIRONMENT_PREFERENCES = [
        ('STRUCTURED', 'Structured'),
        ('UNSTRUCTURED', 'Unstructured'),
        ('OTHER', 'Other'),
    ]
    
    TIMEFRAME_CHOICES = [
        ('THIS_YEAR', 'This Year'),
        ('3_5_YEARS', '3-5 Years'),
    ]

    # Primary keys and relationships
    parent_input_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='parent_inputs')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='submitted_parent_inputs',
                               limit_choices_to={'role': 'PARENT'})
    submission_date = models.DateField(null=False, auto_now_add=True)
    
    # ==================== SECTION A: Background Information ====================
    # Child demographic information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    grade_level = models.CharField(max_length=100, blank=True)
    primary_language = models.CharField(max_length=100, blank=True)
    
    # IEP and parent/guardian information
    iep_start_date = models.DateField(null=True, blank=True)
    parent_guardian_name = models.CharField(max_length=200, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    
    # Medical and diagnostic information
    diagnostic_report_url = models.URLField(blank=True, null=True)
    medical_alerts = models.TextField(blank=True, help_text="Encrypted at rest - important medical information")
    medications = models.TextField(blank=True, help_text="Encrypted at rest - current medications")
    
    # Eligibility criteria (stored as JSON array of selected options)
    eligibility_criteria = models.JSONField(default=list, blank=True, 
                                           help_text="Selected eligibility criteria: Autism Spectrum Disorder, Speech/Language Impairment, ADHD/ADD, Learning Disability, Developmental Delay, Other")
    
    # ==================== SECTION B: Developmental History and Assessment Summary ====================
    # Developmental milestones (in months)
    sat_up_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    crawled_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    walked_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    first_words_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    formed_sentences_age = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # Previous school and services
    previous_school_name = models.CharField(max_length=200, blank=True)
    special_education_services_received = models.BooleanField(default=False)
    has_prior_iep = models.BooleanField(default=False)
    other_prior_services = models.TextField(blank=True, 
                                           help_text="Other services received, e.g., therapy")
    
    # Areas of concern (stored as JSON array of selected options)
    areas_of_concern = models.JSONField(default=list, blank=True,
                                       help_text="Selected areas: Communication, Cognitive Development, Motor Skills, Social Interaction, Behavioral Skills, Emotional Regulation, Sensory Processing, Adaptive Skills")
    
    # ==================== SECTION C: Parent/Guardian Input ====================
    primary_concerns = models.TextField(blank=True, 
                                       help_text="What are your primary concerns about your child?")
    goals_for_child = models.TextField(blank=True,
                                      help_text="What are your goals for your child?")
    strategies_approaches_that_work = models.TextField(blank=True,
                                                      help_text="What strategies/approaches work well with your child?")
    
    # ==================== SECTION D: Behavioral Information ====================
    # Behavioral difficulties (stored as JSON array)
    behavioral_difficulties = models.JSONField(default=list, blank=True,
                                              help_text="Selected difficulties: Transitions, Focusing, Peer interactions")
    
    behavior_description_home_social = models.TextField(blank=True,
                                                       help_text="Describe typical behavior at home and in social settings")
    
    behavior_frustration_triggers = models.TextField(blank=True,
                                                    help_text="Child is often frustrated or anxious due to specific triggers")
    
    triggers_examples = models.TextField(blank=True,
                                        help_text="Examples of triggers")
    
    # Calming strategies (stored as JSON array of selected options)
    calming_strategies_work = models.JSONField(default=list, blank=True,
                                              help_text="Selected strategies: Deep breathing, Sensory tools, Quiet time, Other")
    
    # Communication and social skills
    communication_style = models.CharField(max_length=20, choices=COMMUNICATION_STYLES, blank=True,
                                          help_text="Primary communication method")
    communication_other = models.CharField(max_length=200, blank=True,
                                          help_text="If communication style is Other")
    
    primary_communication_method = models.CharField(max_length=100, blank=True,
                                                   help_text="e.g., Verbal communication, Non-verbal gestures, Other methods")
    
    peer_adult_interaction = models.TextField(blank=True,
                                             help_text="How does your child interact with peers or adults?")
    
    peer_interaction_level = models.TextField(blank=True,
                                             help_text="General peer interaction information")
    
    comfort_environment = models.CharField(max_length=100, blank=True,
                                          help_text="e.g., Structured environments, Unstructured environments, Other")
    
    preferred_environment = models.CharField(max_length=20, choices=ENVIRONMENT_PREFERENCES, blank=True)
    
    # ==================== SECTION E: Sensory and Physical Needs ====================
    # Sensory sensitivities (stored as JSON array of selected options)
    sensory_sensitivities = models.JSONField(default=list, blank=True,
                                            help_text="Selected sensitivities: Noise, Light, Textures, Other")
    
    sensory_sensitivity_other = models.CharField(max_length=200, blank=True,
                                                help_text="If Other sensory sensitivity specified")
    
    # Physical accommodations
    physical_accommodations_needed = models.BooleanField(default=False)
    physical_accommodations_required = models.BooleanField(default=False)
    physical_accommodations_details = models.TextField(blank=True,
                                                      help_text="Describe physical accommodations needed")
    
    # ==================== SECTION F: Goals and Expectations ====================
    # Goals timeframe
    goals_timeframe = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES, blank=True)
    
    # Goals for this year (stored as JSON array of selected options)
    goals_this_year = models.JSONField(default=list, blank=True,
                                      help_text="Selected goals: Academic improvement, Social development, Emotional growth, Other")
    
    # Goals for 3-5 years
    goals_3_5_years = models.TextField(blank=True,
                                      help_text="Specific goals or skills for next 3-5 years")
    
    # ==================== SECTION G: Home Environment and Support ====================
    # Home strategies and routines (stored as JSON array of selected options)
    strategies_routines_home = models.JSONField(default=list, blank=True,
                                               help_text="Selected strategies: Clear schedules, Reward systems, Visual aids, Other")
    
    # Note: home_strategies kept for backwards compatibility but renamed in forms
    home_strategies = models.JSONField(default=list, blank=True,
                                      help_text="[DEPRECATED: Use strategies_routines_home instead]")
    
    # Additional support needs/resources
    additional_support_needs = models.TextField(blank=True,
                                               help_text="[DEPRECATED: Use additional_support_resources_needed instead]")
    
    additional_support_resources_needed = models.TextField(blank=True,
                                                          help_text="What additional support or resources would help at home?")
    
    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Parent Input - {self.child} ({self.submission_date})"


class TeacherInput(models.Model):
    PROGRESS_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ]
    
    teacher_input_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='teacher_inputs')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='submitted_teacher_inputs',
                                limit_choices_to={'role': 'TEACHER'})
    submission_date = models.DateField(null=False, auto_now_add=True)
    
    grade_level = models.CharField(max_length=50, blank=True)
    sessions_attended = models.IntegerField(blank=True, null=True)
    
    # Subject progress tracking
    prewriting_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    prewriting_notes = models.TextField(blank=True)
    
    english_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    english_notes = models.TextField(blank=True)
    
    math_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    math_notes = models.TextField(blank=True)
    
    science_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    science_notes = models.TextField(blank=True)
    
    arts_fine_motor_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    arts_fine_motor_notes = models.TextField(blank=True)
    
    classroom_behavior_progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, blank=True)
    classroom_behavior_notes = models.TextField(blank=True)
    
    overall_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['teacher']),
        ]
    
    def __str__(self):
        return f"Teacher Input - {self.child} ({self.submission_date})"


class SpecialistInput(models.Model):
    SPECIALIST_TYPES = [
        ('OCCUPATIONAL_THERAPY', 'Occupational Therapy'),
        ('SPEECH_LANGUAGE', 'Speech/Language'),
        ('PHYSICAL_THERAPY', 'Physical Therapy'),
        ('BEHAVIORAL_THERAPY', 'Behavioral Therapy'),
        ('ACADEMIC', 'Academic'),
    ]
    
    specialist_input_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='specialist_inputs')
    specialist = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='submitted_specialist_inputs',
                                   limit_choices_to={'role': 'SPECIALIST'})
    submission_date = models.DateField(null=False, auto_now_add=True)
    
    specialist_type = models.CharField(max_length=50, choices=SPECIALIST_TYPES, blank=True)
    areas_of_concern = models.JSONField(default=dict, blank=True)  # JSON object with categories and ratings
    strengths_identified = models.TextField(blank=True)
    disorder_screening_results = models.JSONField(default=dict, blank=True)
    additional_information = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['specialist']),
        ]
    
    def __str__(self):
        return f"{self.get_specialist_type_display()} - {self.child}"


# ==================== SERVICES AND THERAPIES ====================
class ServicesAndTherapies(models.Model):
    SERVICE_TYPES = [
        ('OCCUPATIONAL_THERAPY', 'Occupational Therapy'),
        ('SPEECH_LANGUAGE_THERAPY', 'Speech/Language Therapy'),
        ('PHYSICAL_THERAPY', 'Physical Therapy'),
        ('BEHAVIORAL_THERAPY', 'Behavioral Therapy'),
        ('ACADEMIC_SUPPORT', 'Academic Support'),
        ('OTHER', 'Other'),
    ]
    
    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, null=False)
    service_other_description = models.CharField(max_length=200, blank=True)
    
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='provided_services',
                                  limit_choices_to={'role': 'SPECIALIST'})
    therapist_name = models.CharField(max_length=100, blank=True, help_text="Backup name field")
    
    frequency = models.CharField(max_length=100, null=False, help_text="e.g., '2x per week', '3 times weekly'")
    frequency_days_per_week = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)],
                                                  blank=True, null=True)
    goal_description = models.TextField(blank=True)
    
    start_date = models.DateField(null=False)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.child}"


# ==================== IEP MODELS ====================
class IEP(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived'),
        ('UNDER_REVIEW', 'Under Review'),
    ]
    
    iep_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='ieps')
    iep_start_date = models.DateField(null=False)
    iep_review_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='created_ieps',
                                   limit_choices_to={'role': 'ADMIN'})
    
    is_ai_generated = models.BooleanField(default=True)
    ai_generated_date = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['status']),
        ]
        ordering = ['-iep_start_date']
    
    def __str__(self):
        return f"IEP - {self.child} ({self.iep_start_date})"


class IEPPerformanceLevels(models.Model):
    SKILL_CATEGORIES = [
        ('COGNITIVE_DEVELOPMENT', 'Cognitive Development'),
        ('COMMUNICATION_SKILLS', 'Communication Skills'),
        ('MOTOR_SKILLS', 'Motor Skills'),
        ('SOCIAL_INTERACTION', 'Social Interaction'),
        ('EMOTIONAL_REGULATION', 'Emotional Regulation'),
        ('SENSORY_PROCESSING', 'Sensory Processing'),
    ]
    
    CURRENT_LEVELS = [
        ('PROFICIENT', 'Proficient'),
        ('DEVELOPING', 'Developing'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    ]
    
    performance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iep = models.ForeignKey(IEP, on_delete=models.CASCADE, related_name='performance_levels')
    skill_category = models.CharField(max_length=50, choices=SKILL_CATEGORIES, null=False)
    skill_name = models.CharField(max_length=100)
    current_level = models.CharField(max_length=50, choices=CURRENT_LEVELS, null=False)
    level_description = models.TextField(blank=True)
    assessment_source = models.ForeignKey(Assessment, on_delete=models.SET_NULL, 
                                          null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['iep'])]
    
    def __str__(self):
        return f"{self.skill_name} - {self.get_current_level_display()}"


class IEPGoals(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('IN_PROGRESS', 'In Progress'),
        ('MODIFIED', 'Modified'),
    ]
    
    goal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iep = models.ForeignKey(IEP, on_delete=models.CASCADE, related_name='goals')
    goal_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    goal_statement = models.TextField(null=False)
    goal_category = models.CharField(max_length=100, blank=True, help_text="e.g., Academic, Communication, Motor")
    objectives = models.JSONField(default=list)  # Array of objectives with criteria and timelines
    
    timeframe_months = models.IntegerField(default=10)
    target_completion_date = models.DateField(blank=True, null=True)
    measurement_method = models.TextField(blank=True)
    responsible_personnel = models.JSONField(default=list)  # Array of user IDs
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [models.Index(fields=['iep'])]
        ordering = ['goal_number']
        unique_together = ['iep', 'goal_number']
    
    def __str__(self):
        return f"Goal {self.goal_number}: {self.goal_statement[:50]}"


class IEPObjectives(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('MODIFIED', 'Modified'),
    ]
    
    objective_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(IEPGoals, on_delete=models.CASCADE, related_name='objective_details')
    objective_number = models.IntegerField()
    objective_statement = models.TextField(null=False)
    success_criteria = models.TextField(null=False)
    target_date = models.DateField(blank=True, null=True)
    progress_tracking_method = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['goal'])]
        ordering = ['objective_number']
    
    def __str__(self):
        return f"Objective {self.objective_number}: {self.objective_statement[:50]}"


class PlannedActivitiesServices(models.Model):
    ACTIVITY_TYPES = [
        ('THERAPY', 'Therapy'),
        ('ACADEMIC_SUPPORT', 'Academic Support'),
        ('CLASSROOM_MODIFICATION', 'Classroom Modification'),
    ]
    
    SETTINGS = [
        ('CLASSROOM', 'Classroom'),
        ('PULL_OUT', 'Pull-Out'),
        ('HOME', 'Home'),
        ('COMMUNITY', 'Community'),
        ('OTHER', 'Other'),
    ]
    
    activity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(IEPGoals, on_delete=models.CASCADE, related_name='planned_activities')
    activity_description = models.TextField(null=False)
    activity_type = models.CharField(max_length=100, choices=ACTIVITY_TYPES, blank=True)
    frequency = models.CharField(max_length=100, blank=True, help_text="e.g., '3x per week'")
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., '30 minutes'")
    setting = models.CharField(max_length=50, choices=SETTINGS, blank=True)
    
    responsible_personnel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                              related_name='assigned_activities')
    
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['goal'])]
    
    def __str__(self):
        return f"Activity: {self.activity_description[:50]}"


class Accommodations(models.Model):
    ACCOMMODATION_TYPES = [
        ('CLASSROOM_ACCOMMODATION', 'Classroom Accommodation'),
        ('MODIFICATION', 'Modification'),
        ('ASSISTIVE_TECHNOLOGY', 'Assistive Technology'),
        ('ENVIRONMENTAL', 'Environmental'),
        ('INSTRUCTIONAL', 'Instructional'),
    ]
    
    accommodation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iep = models.ForeignKey(IEP, on_delete=models.CASCADE, related_name='accommodations')
    accommodation_type = models.CharField(max_length=50, choices=ACCOMMODATION_TYPES, null=False)
    accommodation_description = models.TextField(null=False)
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Visual Supports, Extra Time, Sensory Breaks")
    implementation_location = models.CharField(max_length=100, blank=True)
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    implementation_start_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['iep'])]
    
    def __str__(self):
        return f"{self.get_accommodation_type_display()}: {self.accommodation_description[:50]}"


# ==================== WEEKLY PROGRESS REPORTS ====================
class WeeklyProgressReport(models.Model):
    REPORT_TYPES = [
        ('SPECIALIST_INPUT', 'Specialist Input'),
        ('TEACHER_INPUT', 'Teacher Input'),
    ]
    
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='weekly_progress_reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, null=False)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    report_date = models.DateField(null=False)
    week_start_date = models.DateField(null=False)
    week_end_date = models.DateField(null=False)
    
    age = models.IntegerField(blank=True, null=True)
    grade_level = models.CharField(max_length=50, blank=True)
    sessions_attended = models.IntegerField(blank=True, null=True)
    special_needs_type = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['report_date']),
            models.Index(fields=['child', 'report_date']),
        ]
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Weekly Progress - {self.child} ({self.week_start_date})"


class WeeklyServicesProvided(models.Model):
    SERVICE_TYPES = [
        ('OCCUPATIONAL_THERAPY', 'Occupational Therapy'),
        ('SPEECH_LANGUAGE_THERAPY', 'Speech/Language Therapy'),
        ('PHYSICAL_THERAPY', 'Physical Therapy'),
        ('BEHAVIORAL_THERAPY', 'Behavioral Therapy'),
        ('ACADEMIC_SUPPORT', 'Academic Support'),
        ('OTHER', 'Other'),
    ]
    
    service_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(WeeklyProgressReport, on_delete=models.CASCADE, 
                               related_name='services_provided')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, null=False)
    service_other_description = models.CharField(max_length=200, blank=True)
    session_count = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [models.Index(fields=['report'])]
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.session_count} sessions"


class WeeklyGoalsProgress(models.Model):
    STATUS_CHOICES = [
        ('ON_TRACK', 'On Track'),
        ('AHEAD_OF_SCHEDULE', 'Ahead of Schedule'),
        ('BELOW_TARGET', 'Below Target'),
        ('NO_CHANGE', 'No Change'),
    ]
    
    weekly_goal_progress_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(WeeklyProgressReport, on_delete=models.CASCADE,
                               related_name='goal_progress')
    iep_goal = models.ForeignKey(IEPGoals, on_delete=models.CASCADE)
    
    goal_statement = models.TextField(null=False)
    objective_statement = models.TextField(blank=True)
    weekly_progress_description = models.TextField(null=False)
    progress_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                              blank=True, null=True)
    progress_status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['iep_goal']),
        ]
    
    def __str__(self):
        return f"Goal Progress: {self.goal_statement[:50]}"


class WeeklyProgressSummary(models.Model):
    summary_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.OneToOneField(WeeklyProgressReport, on_delete=models.CASCADE,
                                  related_name='summary')
    
    strengths_observed = models.TextField(null=False)
    areas_for_improvement = models.TextField(null=False)
    recommendations_next_week = models.TextField(blank=True)
    therapist_comments = models.TextField(blank=True)
    teacher_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Summary - {self.report.child}"


class ProgressReportAggregate(models.Model):
    aggregate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    iep = models.ForeignKey(IEP, on_delete=models.CASCADE)
    
    report_period_start_date = models.DateField(null=False)
    report_period_end_date = models.DateField(null=False)
    weeks_included = models.IntegerField()
    
    overall_progress_summary = models.TextField(null=False)
    goals_progress_status = models.JSONField(default=dict)  # Summary of all goal progress
    adjustments_recommended = models.TextField(blank=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['child']),
            models.Index(fields=['iep']),
        ]
    
    def __str__(self):
        return f"Aggregate Report - {self.child} ({self.report_period_start_date})"


# ==================== AUDIT & LOGGING ====================
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('SHARE', 'Share'),
    ]
    
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, null=False)
    table_name = models.CharField(max_length=100)
    record_id = models.UUIDField(blank=True, null=True)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    compliance_notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action_type} - {self.table_name} ({self.timestamp})"


class AIGenerationLog(models.Model):
    GENERATION_TYPES = [
        ('IEP_GENERATION', 'IEP Generation'),
        ('GOAL_CREATION', 'Goal Creation'),
        ('PROGRESS_REPORT', 'Progress Report'),
        ('GRAMMAR_CORRECTION', 'Grammar Correction'),
    ]
    
    REVIEW_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('MODIFIED', 'Modified'),
        ('REJECTED', 'Rejected'),
    ]
    
    ai_log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation_type = models.CharField(max_length=50, choices=GENERATION_TYPES, null=False)
    source_data_id = models.UUIDField(blank=True, null=True)
    generated_content_id = models.UUIDField(blank=True, null=True)
    ai_model_version = models.CharField(max_length=100, blank=True)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    human_review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['generation_type'])]
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_generation_type_display()} - {self.generated_at}"
