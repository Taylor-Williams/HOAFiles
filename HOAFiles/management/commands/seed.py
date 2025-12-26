from django.core.management.base import BaseCommand
from HOAFiles.models import User, HOAGroup, House
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed users, HOA groups, and houses'

    def handle(self, *args, **options):

        # -------------------
        # Create Users
        # -------------------
        users_data = [
            {'email': 'user1@example.com', 'password': 'password123'},
            {'email': 'user2@example.com', 'password': 'password123'},
            {'email': 'user3@example.com', 'password': 'password123'},
            {'email': 'user4@example.com', 'password': 'password123'},
            {'email': 'user5@example.com', 'password': 'password123'},
        ]

        users = []

        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                username=data['email'],
            )

            if created:
                user.set_password(data['password'])  # Hash the password properly
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {user.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.email} already exists"))

            users.append(user)

        # -------------------
        # Create HOA Groups
        # -------------------
        hoa_groups_data = [
            {'name': 'Sunset HOA', 'owner_email': 'owner1@hoa.com'},
            {'name': 'Lakeview HOA', 'owner_email': 'owner2@hoa.com'},
        ]

        hoa_groups = []

        for data in hoa_groups_data:
            hoa, created = HOAGroup.objects.get_or_create(
                name=data['name'],
                defaults={'owner_email': data['owner_email']}
            )

            hoa.users.add(*users[:3])  # first 3 users
            hoa_groups.append(hoa)

            self.stdout.write(self.style.SUCCESS(f"HOA Group seeded: {hoa.name}"))

        # -------------------
        # Create Houses
        # -------------------
        houses_data = [
            '123 Main St',
            '456 Oak Ave',
            '789 Pine Rd',
        ]

        for address in houses_data:
            house, created = House.objects.get_or_create(address=address)

            # Assign users to houses
            house.users.add(users[0], users[1])

            self.stdout.write(self.style.SUCCESS(f"House seeded: {address}"))

        self.stdout.write(
            self.style.SUCCESS("\nSeeding complete: users, HOA groups, and houses created.")
        )

