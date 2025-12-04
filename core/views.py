from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from core.models import (
    User, Child, ChildrenEligibility, DevelopmentalHistory,
    Assessment, AssessmentSkillArea, DisorderScreening,
    ParentInput, TeacherInput, SpecialistInput,
    ServicesAndTherapies, IEP, IEPPerformanceLevels,
    IEPGoals, IEPObjectives, PlannedActivitiesServices,
    Accommodations, WeeklyProgressReport, WeeklyServicesProvided,
    WeeklyGoalsProgress, WeeklyProgressSummary, ProgressReportAggregate,
    AuditLog, AIGenerationLog, AssessmentRequest
)
from core.serializers import (
    UserSerializer, UserCreateSerializer, ChildSerializer,
    ChildrenEligibilitySerializer, DevelopmentalHistorySerializer,
    AssessmentSerializer, AssessmentSkillAreaSerializer,
    DisorderScreeningSerializer, ParentInputSerializer,
    TeacherInputSerializer, SpecialistInputSerializer,
    ServicesAndTherapiesSerializer, IEPSerializer, IEPPerformanceLevelsSerializer,
    IEPGoalsSerializer, IEPObjectivesSerializer,
    PlannedActivitiesServicesSerializer, AccommodationsSerializer,
    WeeklyProgressReportSerializer, WeeklyServicesProvidedSerializer,
    WeeklyGoalsProgressSerializer, WeeklyProgressSummarySerializer,
    ProgressReportAggregateSerializer, AuditLogSerializer,
    AIGenerationLogSerializer, SpecialistListSerializer, AssessmentRequestSerializer
)


# ==================== USER VIEWSET ====================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['created_at', 'email', 'first_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Get users filtered by role"""
        role = request.query_params.get('role')
        if role:
            users = User.objects.filter(role=role)
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        return Response({'error': 'role parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
class SpecialistDirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only directory of specialists for parent booking / selection.
    """
    serializer_class = SpecialistListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "specialization"]
    ordering_fields = ["first_name", "last_name", "years_experience", "created_at"]
    ordering = ["first_name"]

    def get_queryset(self):
        qs = User.objects.filter(role="SPECIALIST", is_active=True)
        # Optional: only show those accepting new assessments if field exists
        if hasattr(User, "accepts_new_assessments"):
            qs = qs.filter(accepts_new_assessments=True)
        specialization = self.request.query_params.get("specialization")
        if specialization:
            qs = qs.filter(specialization__iexact=specialization)
        return qs


# ==================== CHILD VIEWSET ====================
class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'grade_level', 'parent']
    search_fields = ['first_name', 'last_name', 'primary_language']
    ordering_fields = ['date_of_birth', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter children based on user role"""
        queryset = Child.objects.all()
        user = self.request.user
        
        if user.role == 'PARENT':
            queryset = queryset.filter(
                Q(parent=user) | Q(secondary_parent=user)
            )
        elif user.role == 'SPECIALIST':
            # Specialists can see children they work with
            child_ids = ServicesAndTherapies.objects.filter(
                therapist=user
            ).values_list('child_id', flat=True)
            queryset = queryset.filter(child_id__in=child_ids)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get all assessments for a child"""
        child = self.get_object()
        assessments = child.assessments.all()
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ieps(self, request, pk=None):
        """Get all IEPs for a child"""
        child = self.get_object()
        ieps = child.ieps.all()
        serializer = IEPSerializer(ieps, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """Get all services for a child"""
        child = self.get_object()
        services = child.services.filter(is_active=True)
        serializer = ServicesAndTherapiesSerializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress_reports(self, request, pk=None):
        """Get all progress reports for a child"""
        child = self.get_object()
        reports = child.weekly_progress_reports.all()
        serializer = WeeklyProgressReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def eligibilities(self, request, pk=None):
        """Get all eligibilities for a child"""
        child = self.get_object()
        eligibilities = child.eligibilities.all()
        serializer = ChildrenEligibilitySerializer(eligibilities, many=True)
        return Response(serializer.data)


# ==================== ASSESSMENT REQUEST VIEWSET ====================
class AssessmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AssessmentRequest.objects.all()
    serializer_class = AssessmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["child", "specialist", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == "PARENT":
            return qs.filter(parent=user)
        if user.role == "SPECIALIST":
            return qs.filter(specialist=user)
        # Admin/others see all
        return qs

    # Admin can approve / reject
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        obj = self.get_object()
        obj.status = "APPROVED"
        obj.save(update_fields=["status"])
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        obj = self.get_object()
        obj.status = "REJECTED"
        obj.save(update_fields=["status"])
        return Response({"status": "rejected"})
    

# ==================== CHILD ELIGIBILITY VIEWSET ====================
class ChildrenEligibilityViewSet(viewsets.ModelViewSet):
    queryset = ChildrenEligibility.objects.all()
    serializer_class = ChildrenEligibilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child', 'eligibility_type']
    ordering_fields = ['date_identified', 'created_at']


# ==================== DEVELOPMENTAL HISTORY VIEWSET ====================
class DevelopmentalHistoryViewSet(viewsets.ModelViewSet):
    queryset = DevelopmentalHistory.objects.all()
    serializer_class = DevelopmentalHistorySerializer
    permission_classes = [permissions.IsAuthenticated]


# ==================== ASSESSMENT VIEWSET ====================
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['child', 'assessment_type', 'is_complete']
    search_fields = ['child__first_name', 'child__last_name']
    ordering_fields = ['assessment_date', 'created_at']
    ordering = ['-assessment_date']
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark assessment as complete"""
        assessment = self.get_object()
        assessment.is_complete = True
        assessment.save()
        return Response({'status': 'Assessment marked as complete'})


# ==================== ASSESSMENT SKILL AREA VIEWSET ====================
class AssessmentSkillAreaViewSet(viewsets.ModelViewSet):
    queryset = AssessmentSkillArea.objects.all()
    serializer_class = AssessmentSkillAreaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assessment', 'category', 'rating']


# ==================== DISORDER SCREENING VIEWSET ====================
class DisorderScreeningViewSet(viewsets.ModelViewSet):
    queryset = DisorderScreening.objects.all()
    serializer_class = DisorderScreeningSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assessment', 'disorder_type', 'risk_level']


# ==================== PARENT INPUT VIEWSET ====================
class ParentInputViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ParentInput with automatic Child creation and edit support
    """
    serializer_class = ParentInputSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # ✅ ADD THESE FOUR LINES
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child']  # Enable filtering: GET /parent-inputs/?child=123
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']  # Most recent first
    
    def get_queryset(self):
        """Filter by current user (parent) + auto-set intake_status"""
        user = self.request.user
        queryset = ParentInput.objects.filter(parent=user)
        
        # ✅ Auto-set intake_status based on completion
        for obj in queryset:
            if obj.intake_status != 'completed':
                # Check if form looks complete
                is_complete = bool(
                    obj.child and 
                    obj.first_name and 
                    obj.last_name
                )
                if is_complete:
                    obj.intake_status = 'completed'
                    obj.save(update_fields=['intake_status'])
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get the latest parent input for the current user
        Returns completion status based on submission_date
        """
        try:
            parent_input = ParentInput.objects.filter(
                parent=request.user
            ).latest('submission_date')
            
            is_complete = bool(
                parent_input.child and
                parent_input.first_name and
                parent_input.last_name
            )
            
            status_str = 'completed' if is_complete else 'in-progress'
            
            return Response({
                'id': str(parent_input.parent_input_id),
                'status': status_str,
                'child_id': str(parent_input.child.child_id) if parent_input.child else None,
                'submission_date': parent_input.submission_date,
                'updated_at': parent_input.updated_at,
            })
        except ParentInput.DoesNotExist:
            return Response({
                'id': None,
                'status': 'pending',
                'child_id': None,
                'submission_date': None,
                'updated_at': None,
            })

    def create(self, request, *args, **kwargs):
        """
        Override create to:
        1. Extract child data
        2. Create or get Child record
        3. Set child_id in ParentInput
        4. Save ParentInput
        """
        try:
            data = request.data.copy()
            
            # Extract child information
            first_name = data.get('childFirstName') or data.get('first_name')
            last_name = data.get('childLastName') or data.get('last_name')
            date_of_birth = data.get('dob') or data.get('date_of_birth')
            gender = data.get('gender', 'OTHER')
            grade_level = data.get('gradeLevel') or data.get('grade_level', 'Not specified')
            primary_language = data.get('primaryLanguage') or data.get('primary_language', 'English')

            # ✅ SANITIZE ALL FIELDS
            for key in list(data.keys()):
                value = data[key]
                if isinstance(value, list):
                    data[key] = value[0] if value else None

            # Validate required child fields
            if not first_name or not last_name:
                return Response(
                    {'error': 'Child first_name and last_name are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ Create Child record
            child, created = Child.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                defaults={
                    'gender': gender,
                    'grade_level': grade_level,
                    'primary_language': primary_language,
                    'parent': request.user,
                    'intake_status': 'completed',  # ✅ Set on Child
                    'assessment_status': 'for_assessment',  # ✅ After intake
                }
            )
            
            print(f"[ParentInput] Child {'created' if created else 'retrieved'}: {child}")
            
            # ✅ Add child_id and parent_id to data
            data['child'] = str(child.child_id)
            data['parent'] = str(request.user.user_id)
            
            # ✅ DO NOT set these - they're on Child model, not ParentInput
            # Remove them if they're in data
            data.pop('intake_status', None)
            data.pop('assessment_status', None)
            data.pop('assessment_scheduled_date', None)
            data.pop('enrollment_status', None)
            
            # ✅ HANDLE NEW FIELDS - Set defaults for optional fields
            if not data.get('prior_services'):
                data['prior_services'] = []
            if not data.get('motor_needs'):
                data['motor_needs'] = []
            if not data.get('child_strengths'):
                data['child_strengths'] = []
            
            print(f"[ParentInput] Data after processing: {data}")
            
            # Create serializer with updated data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"[ParentInput] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error creating parent input: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

def perform_create(self, serializer):
    """✅ Only set intake_status on ParentInput, not on Child"""
    serializer.save(intake_status='completed')

    
    def perform_create(self, serializer):
        """✅ UPDATED: Auto-set intake_status to 'completed' on creation"""
        serializer.save(intake_status='completed')
    
    def perform_update(self, serializer):
        """✅ NEW: Handle PATCH requests to update existing ParentInput"""
        print(f"[ParentInput] Updating: {serializer.instance.parent_input_id}")
        serializer.save(intake_status='completed')


# ==================== TEACHER INPUT VIEWSET ====================
class TeacherInputViewSet(viewsets.ModelViewSet):
    queryset = TeacherInput.objects.all()
    serializer_class = TeacherInputSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child', 'teacher']
    ordering_fields = ['submission_date', 'created_at']
    ordering = ['-submission_date']


# ==================== SPECIALIST INPUT VIEWSET ====================
class SpecialistInputViewSet(viewsets.ModelViewSet):
    queryset = SpecialistInput.objects.all()
    serializer_class = SpecialistInputSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['child', 'specialist', 'specialist_type']


# ==================== SERVICES & THERAPIES VIEWSET ====================
class ServicesAndTherapiesViewSet(viewsets.ModelViewSet):
    queryset = ServicesAndTherapies.objects.all()
    serializer_class = ServicesAndTherapiesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child', 'therapist', 'service_type', 'is_active']
    ordering_fields = ['start_date', 'created_at']
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a service"""
        service = self.get_object()
        service.is_active = False
        service.end_date = timezone.now().date()
        service.save()
        return Response({'status': 'Service deactivated'})


# ==================== IEP VIEWSET ====================
class IEPViewSet(viewsets.ModelViewSet):
    queryset = IEP.objects.all()
    serializer_class = IEPSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['child', 'status', 'is_ai_generated']
    search_fields = ['child__first_name', 'child__last_name']
    ordering_fields = ['iep_start_date', 'created_at']
    ordering = ['-iep_start_date']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an IEP (change status to ACTIVE)"""
        iep = self.get_object()
        iep.status = 'ACTIVE'
        iep.save()
        return Response({'status': 'IEP activated'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive an IEP"""
        iep = self.get_object()
        iep.status = 'ARCHIVED'
        iep.save()
        return Response({'status': 'IEP archived'})
    
    @action(detail=True, methods=['get'])
    def goals(self, request, pk=None):
        """Get all goals for an IEP"""
        iep = self.get_object()
        goals = iep.goals.all()
        serializer = IEPGoalsSerializer(goals, many=True)
        return Response(serializer.data)


# ==================== IEP GOALS VIEWSET ====================
class IEPGoalsViewSet(viewsets.ModelViewSet):
    queryset = IEPGoals.objects.all()
    serializer_class = IEPGoalsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['iep', 'status', 'goal_category']
    ordering_fields = ['goal_number', 'target_completion_date']


# ==================== IEP PERFORMANCE LEVELS VIEWSET ====================
class IEPPerformanceLevelsViewSet(viewsets.ModelViewSet):
    queryset = IEPPerformanceLevels.objects.all()
    serializer_class = IEPPerformanceLevelsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['iep', 'skill_category', 'current_level']


# ==================== ACCOMMODATIONS VIEWSET ====================
class AccommodationsViewSet(viewsets.ModelViewSet):
    queryset = Accommodations.objects.all()
    serializer_class = AccommodationsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['iep', 'accommodation_type']


# ==================== WEEKLY PROGRESS REPORT VIEWSET ====================
class WeeklyProgressReportViewSet(viewsets.ModelViewSet):
    queryset = WeeklyProgressReport.objects.all()
    serializer_class = WeeklyProgressReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child', 'report_type', 'submitted_by']
    ordering_fields = ['report_date', 'created_at']
    ordering = ['-report_date']
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """Get services provided in this report"""
        report = self.get_object()
        services = report.services_provided.all()
        serializer = WeeklyServicesProvidedSerializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def goal_progress(self, request, pk=None):
        """Get goal progress in this report"""
        report = self.get_object()
        progress = report.goal_progress.all()
        serializer = WeeklyGoalsProgressSerializer(progress, many=True)
        return Response(serializer.data)


# ==================== PROGRESS REPORT AGGREGATE VIEWSET ====================
class ProgressReportAggregateViewSet(viewsets.ModelViewSet):
    queryset = ProgressReportAggregate.objects.all()
    serializer_class = ProgressReportAggregateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['child', 'iep']
    ordering_fields = ['report_period_start_date', 'generated_at']


# ==================== AUDIT LOG VIEWSET ====================
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action_type', 'table_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


# ==================== AI GENERATION LOG VIEWSET ====================
class AIGenerationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIGenerationLog.objects.all()
    serializer_class = AIGenerationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['generation_type', 'human_review_status']
    ordering_fields = ['generated_at']
    ordering = ['-generated_at']
