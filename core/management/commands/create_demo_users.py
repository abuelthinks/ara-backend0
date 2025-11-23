from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for all roles'

    def handle(self, *args, **options):
        password = 'password123'
        
        # Demo users with their roles
        demo_users = [
            {
                'username': 'parent',
                'email': 'parent@demo.com',
                'first_name': 'Demo',
                'last_name': 'Parent',
                'role': 'PARENT',
            },
            {
                'username': 'specialist',
                'email': 'specialist@demo.com',
                'first_name': 'Demo',
                'last_name': 'Specialist',
                'role': 'SPECIALIST',
            },
            {
                'username': 'admin',
                'email': 'admin@demo.com',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'role': 'ADMIN',
            },
            {
                'username': 'teacher',
                'email': 'teacher@demo.com',
                'first_name': 'Demo',
                'last_name': 'Teacher',
                'role': 'TEACHER',
            },
        ]

        for user_data in demo_users:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Skipping.')
                )
                continue

            # Create the user
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],  # Adjust if your User model has a role field
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created user: {username} ({user_data["role"]}) with password: {password}'
                )
            )

        self.stdout.write(self.style.SUCCESS('Demo users created successfully!'))
