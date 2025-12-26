from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from HOAFiles.models import User, HOAGroup, House, HOAMembership
import sys


class UserModelTest(TestCase):
    """Test suite for the User model"""

    def setUp(self):
        """Set up test data"""
        self.user_email = 'test@example.com'
        self.user_password = 'testpassword123'
    
    def _notify_success(self, message):
        """Print a success notification"""
        print(f"\n✓ PASSED: {message}", file=sys.stderr)

    def test_user_creation(self):
        """Test creating a user with email and password"""
        user = User(email=self.user_email)
        user.set_password(self.user_password)
        user.save()
        
        self.assertEqual(user.email, self.user_email)
        self.assertIsNotNone(user.password)
        self.assertNotEqual(user.password, self.user_password)  # Password should be hashed
        self._notify_success("User creation: Successfully created user with email and hashed password")

    def test_user_email_uniqueness(self):
        """Test that email must be unique"""
        user1 = User(email=self.user_email)
        user1.set_password(self.user_password)
        user1.save()
        
        # Try to create another user with the same email
        user2 = User(email=self.user_email)
        user2.set_password('differentpassword')
        
        with self.assertRaises(IntegrityError):
            user2.save()
        self._notify_success("Email uniqueness: Confirmed that duplicate emails are prevented by database constraint")

    def test_set_password_hashes_password(self):
        """Test that set_password properly hashes the password"""
        user = User(email=self.user_email)
        raw_password = 'plaintextpassword'
        user.set_password(raw_password)
        
        # Password should be hashed (not plain text)
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.password.startswith('pbkdf2_'))  # Django's default hasher
        self._notify_success("Password hashing: Verified that set_password() properly hashes passwords using Django's pbkdf2 algorithm")

    def test_check_password_correct(self):
        """Test that check_password returns True for correct password"""
        user = User(email=self.user_email)
        user.set_password(self.user_password)
        user.save()
        
        # Reload from database to ensure password is saved
        user = User.objects.get(email=self.user_email)
        self.assertTrue(user.check_password(self.user_password))
        self._notify_success("Password verification: Confirmed check_password() correctly validates matching passwords")

    def test_check_password_incorrect(self):
        """Test that check_password returns False for incorrect password"""
        user = User(email=self.user_email)
        user.set_password(self.user_password)
        user.save()
        
        # Reload from database
        user = User.objects.get(email=self.user_email)
        self.assertFalse(user.check_password('wrongpassword'))
        self._notify_success("Password security: Verified that incorrect passwords are properly rejected")

    def test_user_str_method(self):
        """Test the __str__ method returns the email"""
        user = User(email=self.user_email)
        user.set_password(self.user_password)
        user.save()
        
        self.assertEqual(str(user), self.user_email)
        self._notify_success("String representation: Verified __str__() method returns user's email address")

    def test_user_email_field_required(self):
        """Test that email field is required"""
        user = User()
        user.set_password(self.user_password)
        
        with self.assertRaises(ValidationError):
            user.full_clean()
        self._notify_success("Field validation: Confirmed that email field is required and validated")


class HOAGroupModelTest(TestCase):
    """Test suite for the HOAGroup model"""

    def setUp(self):
        """Set up test data"""
        self.group_name = 'Sunset Community HOA'
        self.owner_email = 'owner@example.com'
        
        # Create a user for the owner
        self.owner = User(email=self.owner_email)
        self.owner.set_password('password123')
        self.owner.save()
        
        # Create additional users
        self.user1 = User(email='user1@example.com')
        self.user1.set_password('password123')
        self.user1.save()
        
        self.user2 = User(email='user2@example.com')
        self.user2.set_password('password123')
        self.user2.save()
    
    def _notify_success(self, message):
        """Print a success notification"""
        print(f"\n✓ PASSED: {message}", file=sys.stderr)

    def test_hoa_group_creation(self):
        """Test creating an HOA group"""
        group = HOAGroup(name=self.group_name, owner_email=self.owner_email)
        group.save()
        
        self.assertEqual(group.name, self.group_name)
        self.assertEqual(group.owner_email, self.owner_email)
        self._notify_success("HOA Group creation: Successfully created HOA group with name and owner email")

    def test_hoa_group_owner_email_uniqueness(self):
        """Test that owner_email must be unique"""
        group1 = HOAGroup(name='Group 1', owner_email=self.owner_email)
        group1.save()
        
        # Try to create another group with the same owner_email
        group2 = HOAGroup(name='Group 2', owner_email=self.owner_email)
        
        with self.assertRaises(IntegrityError):
            group2.save()
        self._notify_success("Owner email uniqueness: Confirmed that each HOA group must have a unique owner email")

    def test_hoa_group_many_to_many_users(self):
        """Test adding users to an HOA group via many-to-many relationship"""
        group = HOAGroup(name=self.group_name, owner_email=self.owner_email)
        group.save()
        
        # Add users to the group
        group.users.add(self.user1, self.user2)
        
        # Check that users are added
        self.assertEqual(group.users.count(), 2)
        self.assertIn(self.user1, group.users.all())
        self.assertIn(self.user2, group.users.all())
        self._notify_success("Many-to-many relationship: Successfully added multiple users to HOA group via M2M field")

    def test_hoa_group_related_name(self):
        """Test that users can access their HOA groups via related_name"""
        group = HOAGroup(name=self.group_name, owner_email=self.owner_email)
        group.save()
        group.users.add(self.user1)
        
        # Reload user to get related objects
        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.hoa_groups.count(), 1)
        self.assertIn(group, user.hoa_groups.all())
        self._notify_success("Related name access: Verified users can access their HOA groups via 'hoa_groups' related_name")

    def test_hoa_group_remove_users(self):
        """Test removing users from an HOA group"""
        group = HOAGroup(name=self.group_name, owner_email=self.owner_email)
        group.save()
        group.users.add(self.user1, self.user2)
        
        # Remove a user
        group.users.remove(self.user1)
        
        self.assertEqual(group.users.count(), 1)
        self.assertNotIn(self.user1, group.users.all())
        self.assertIn(self.user2, group.users.all())
        self._notify_success("User removal: Successfully removed users from HOA group while maintaining other relationships")

    def test_hoa_group_str_method(self):
        """Test the __str__ method returns the group name"""
        group = HOAGroup(name=self.group_name, owner_email=self.owner_email)
        group.save()
        
        self.assertEqual(str(group), self.group_name)
        self._notify_success("String representation: Verified __str__() method returns HOA group name")

    def test_hoa_group_name_field_required(self):
        """Test that name field is required"""
        group = HOAGroup(owner_email=self.owner_email)
        
        with self.assertRaises(ValidationError):
            group.full_clean()
        self._notify_success("Field validation: Confirmed that HOA group name field is required")

    def test_hoa_group_owner_email_field_required(self):
        """Test that owner_email field is required"""
        group = HOAGroup(name=self.group_name)
        
        with self.assertRaises(ValidationError):
            group.full_clean()
        self._notify_success("Field validation: Confirmed that HOA group owner_email field is required")


class HouseModelTest(TestCase):
    """Test suite for the House model"""

    def setUp(self):
        """Set up test data"""
        self.house_address = '123 Main Street, Anytown, ST 12345'
        
        # Create users
        self.user1 = User(email='user1@example.com')
        self.user1.set_password('password123')
        self.user1.save()
        
        self.user2 = User(email='user2@example.com')
        self.user2.set_password('password123')
        self.user2.save()
        
        self.user3 = User(email='user3@example.com')
        self.user3.set_password('password123')
        self.user3.save()
    
    def _notify_success(self, message):
        """Print a success notification"""
        print(f"\n✓ PASSED: {message}", file=sys.stderr)

    def test_house_creation(self):
        """Test creating a house"""
        house = House(address=self.house_address)
        house.save()
        
        self.assertEqual(house.address, self.house_address)
        self._notify_success("House creation: Successfully created house with address")

    def test_house_address_uniqueness(self):
        """Test that address must be unique"""
        house1 = House(address=self.house_address)
        house1.save()
        
        # Try to create another house with the same address
        house2 = House(address=self.house_address)
        
        with self.assertRaises(IntegrityError):
            house2.save()
        self._notify_success("Address uniqueness: Confirmed that duplicate addresses are prevented by database constraint")

    def test_house_many_to_many_users(self):
        """Test adding users to a house via many-to-many relationship"""
        house = House(address=self.house_address)
        house.save()
        
        # Add users to the house
        house.users.add(self.user1, self.user2)
        
        # Check that users are added
        self.assertEqual(house.users.count(), 2)
        self.assertIn(self.user1, house.users.all())
        self.assertIn(self.user2, house.users.all())
        self._notify_success("Many-to-many relationship: Successfully added multiple users to house via M2M field")

    def test_house_related_name(self):
        """Test that users can access their houses via related_name"""
        house = House(address=self.house_address)
        house.save()
        house.users.add(self.user1)
        
        # Reload user to get related objects
        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.houses.count(), 1)
        self.assertIn(house, user.houses.all())
        self._notify_success("Related name access: Verified users can access their houses via 'houses' related_name")

    def test_house_remove_users(self):
        """Test removing users from a house"""
        house = House(address=self.house_address)
        house.save()
        house.users.add(self.user1, self.user2, self.user3)
        
        # Remove a user
        house.users.remove(self.user1)
        
        self.assertEqual(house.users.count(), 2)
        self.assertNotIn(self.user1, house.users.all())
        self.assertIn(self.user2, house.users.all())
        self.assertIn(self.user3, house.users.all())
        self._notify_success("User removal: Successfully removed users from house while maintaining other relationships")

    def test_house_clear_users(self):
        """Test clearing all users from a house"""
        house = House(address=self.house_address)
        house.save()
        house.users.add(self.user1, self.user2, self.user3)
        
        # Clear all users
        house.users.clear()
        
        self.assertEqual(house.users.count(), 0)
        self._notify_success("Clear users: Successfully cleared all users from house using clear() method")

    def test_house_str_method(self):
        """Test the __str__ method returns the address"""
        house = House(address=self.house_address)
        house.save()
        
        self.assertEqual(str(house), self.house_address)
        self._notify_success("String representation: Verified __str__() method returns house address")

    def test_house_address_field_required(self):
        """Test that address field is required"""
        house = House()
        
        with self.assertRaises(ValidationError):
            house.full_clean()
        self._notify_success("Field validation: Confirmed that house address field is required")

    def test_user_can_have_multiple_houses(self):
        """Test that a user can be associated with multiple houses"""
        house1 = House(address='123 Main St')
        house1.save()
        house2 = House(address='456 Oak Ave')
        house2.save()
        
        house1.users.add(self.user1)
        house2.users.add(self.user1)
        
        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.houses.count(), 2)
        self._notify_success("Multiple relationships: Verified that a single user can be associated with multiple houses")

    def test_house_can_have_multiple_users(self):
        """Test that a house can be associated with multiple users"""
        house = House(address=self.house_address)
        house.save()
        
        house.users.add(self.user1, self.user2, self.user3)
        
        self.assertEqual(house.users.count(), 3)
        self._notify_success("Multiple relationships: Verified that a single house can be associated with multiple users")


class ModelRelationshipsTest(TestCase):
    """Test suite for cross-model relationships"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.user1 = User(email='user1@example.com')
        self.user1.set_password('password123')
        self.user1.save()
        
        self.user2 = User(email='user2@example.com')
        self.user2.set_password('password123')
        self.user2.save()
        
        # Create HOA group
        self.hoa_group = HOAGroup(name='Test HOA', owner_email='owner@example.com')
        self.hoa_group.save()
        
        # Create house
        self.house = House(address='123 Test Street')
        self.house.save()
    
    def _notify_success(self, message):
        """Print a success notification"""
        print(f"\n✓ PASSED: {message}", file=sys.stderr)

    def test_user_in_multiple_relationships(self):
        """Test that a user can be in both HOA groups and houses"""
        self.hoa_group.users.add(self.user1)
        self.house.users.add(self.user1)
        
        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.hoa_groups.count(), 1)
        self.assertEqual(user.houses.count(), 1)
        self._notify_success("Cross-model relationships: Verified user can simultaneously belong to HOA groups and houses")

    def test_complex_relationships(self):
        """Test complex relationships between all models"""
        # Add users to HOA group
        self.hoa_group.users.add(self.user1, self.user2)
        
        # Add users to house
        self.house.users.add(self.user1)
        
        # Verify relationships
        self.assertEqual(self.hoa_group.users.count(), 2)
        self.assertEqual(self.house.users.count(), 1)
        
        user1 = User.objects.get(email=self.user1.email)
        self.assertEqual(user1.hoa_groups.count(), 1)
        self.assertEqual(user1.houses.count(), 1)
        
        user2 = User.objects.get(email=self.user2.email)
        self.assertEqual(user2.hoa_groups.count(), 1)
        self.assertEqual(user2.houses.count(), 0)
        self._notify_success("Complex relationships: Successfully tested intricate many-to-many relationships across all three models")


class HOAMembershipModelTest(TestCase):
    """Test suite for the HOAMembership model"""

    def setUp(self):
        """Set up test data"""
        self.owner = User(email='owner@example.com', username='owner')
        self.owner.set_password('password123')
        self.owner.save()

        self.user1 = User(email='user1@example.com', username='user1')
        self.user1.set_password('password123')
        self.user1.save()

        self.user2 = User(email='user2@example.com', username='user2')
        self.user2.set_password('password123')
        self.user2.save()

        self.hoa_group = HOAGroup(name='Test HOA', owner_email='owner@example.com')
        self.hoa_group.save()

    def _notify_success(self, message):
        """Print a success notification"""
        print(f"\n✓ PASSED: {message}", file=sys.stderr)

    def test_membership_creation_with_default_role(self):
        """Test creating a membership with default 'member' role"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership.save()

        self.assertEqual(membership.user, self.user1)
        self.assertEqual(membership.hoa_group, self.hoa_group)
        self.assertEqual(membership.role, 'member')
        self.assertIsNotNone(membership.joined_at)
        self._notify_success("Membership creation: Successfully created membership with default 'member' role")

    def test_membership_creation_with_admin_role(self):
        """Test creating a membership with 'admin' role"""
        membership = HOAMembership(user=self.owner, hoa_group=self.hoa_group, role='admin')
        membership.save()

        self.assertEqual(membership.role, 'admin')
        self._notify_success("Admin membership: Successfully created membership with 'admin' role")

    def test_membership_joined_at_auto_set(self):
        """Test that joined_at is automatically set on creation"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership.save()

        self.assertIsNotNone(membership.joined_at)
        self._notify_success("Auto timestamp: Verified joined_at is automatically set on creation")

    def test_membership_str_method(self):
        """Test the __str__ method returns proper format"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group, role='member')
        membership.save()

        expected_str = f"{self.user1.email} - {self.hoa_group.name} (member)"
        self.assertEqual(str(membership), expected_str)
        self._notify_success("String representation: Verified __str__() returns 'email - group_name (role)' format")

    def test_membership_unique_together_constraint(self):
        """Test that a user can only have one membership per HOA group"""
        membership1 = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership1.save()

        # Try to create another membership for the same user in the same group
        membership2 = HOAMembership(user=self.user1, hoa_group=self.hoa_group, role='admin')

        with self.assertRaises(IntegrityError):
            membership2.save()
        self._notify_success("Unique constraint: Confirmed user can only have one membership per HOA group")

    def test_membership_user_required(self):
        """Test that user field is required"""
        membership = HOAMembership(hoa_group=self.hoa_group)

        with self.assertRaises(IntegrityError):
            membership.save()
        self._notify_success("Field validation: Confirmed that user field is required")

    def test_membership_hoa_group_required(self):
        """Test that hoa_group field is required"""
        membership = HOAMembership(user=self.user1)

        with self.assertRaises(IntegrityError):
            membership.save()
        self._notify_success("Field validation: Confirmed that hoa_group field is required")

    def test_membership_cascade_delete_user(self):
        """Test that membership is deleted when user is deleted"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership.save()
        membership_id = membership.id

        self.user1.delete()

        self.assertFalse(HOAMembership.objects.filter(id=membership_id).exists())
        self._notify_success("Cascade delete: Verified membership is deleted when user is deleted")

    def test_membership_cascade_delete_hoa_group(self):
        """Test that membership is deleted when HOA group is deleted"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership.save()
        membership_id = membership.id

        self.hoa_group.delete()

        self.assertFalse(HOAMembership.objects.filter(id=membership_id).exists())
        self._notify_success("Cascade delete: Verified membership is deleted when HOA group is deleted")

    def test_user_can_have_multiple_memberships(self):
        """Test that a user can be a member of multiple HOA groups"""
        hoa_group2 = HOAGroup(name='Second HOA', owner_email='owner2@example.com')
        hoa_group2.save()

        membership1 = HOAMembership(user=self.user1, hoa_group=self.hoa_group)
        membership1.save()
        membership2 = HOAMembership(user=self.user1, hoa_group=hoa_group2)
        membership2.save()

        self.assertEqual(self.user1.hoa_memberships.count(), 2)
        self._notify_success("Multiple memberships: Verified user can belong to multiple HOA groups")

    def test_hoa_group_can_have_multiple_members(self):
        """Test that an HOA group can have multiple members"""
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')
        HOAMembership.objects.create(user=self.user2, hoa_group=self.hoa_group, role='member')
        HOAMembership.objects.create(user=self.owner, hoa_group=self.hoa_group, role='admin')

        self.assertEqual(self.hoa_group.memberships.count(), 3)
        self._notify_success("Multiple members: Verified HOA group can have multiple members")

    def test_hoa_group_is_admin_method(self):
        """Test the is_admin() method on HOAGroup"""
        HOAMembership.objects.create(user=self.owner, hoa_group=self.hoa_group, role='admin')
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')

        self.assertTrue(self.hoa_group.is_admin(self.owner))
        self.assertFalse(self.hoa_group.is_admin(self.user1))
        self.assertFalse(self.hoa_group.is_admin(self.user2))  # Not a member at all
        self._notify_success("is_admin method: Verified HOAGroup.is_admin() correctly identifies admin users")

    def test_hoa_group_get_user_role_method(self):
        """Test the get_user_role() method on HOAGroup"""
        HOAMembership.objects.create(user=self.owner, hoa_group=self.hoa_group, role='admin')
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')

        self.assertEqual(self.hoa_group.get_user_role(self.owner), 'admin')
        self.assertEqual(self.hoa_group.get_user_role(self.user1), 'member')
        self.assertIsNone(self.hoa_group.get_user_role(self.user2))  # Not a member
        self._notify_success("get_user_role method: Verified HOAGroup.get_user_role() returns correct role or None")

    def test_membership_related_name_from_user(self):
        """Test accessing memberships from user via related_name"""
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')

        user = User.objects.get(email=self.user1.email)
        self.assertEqual(user.hoa_memberships.count(), 1)
        self.assertEqual(user.hoa_memberships.first().hoa_group, self.hoa_group)
        self._notify_success("Related name (user): Verified accessing memberships via user.hoa_memberships")

    def test_membership_related_name_from_hoa_group(self):
        """Test accessing memberships from HOA group via related_name"""
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')

        group = HOAGroup.objects.get(name=self.hoa_group.name)
        self.assertEqual(group.memberships.count(), 1)
        self.assertEqual(group.memberships.first().user, self.user1)
        self._notify_success("Related name (group): Verified accessing memberships via hoa_group.memberships")

    def test_membership_role_choices(self):
        """Test that role field only accepts valid choices"""
        membership = HOAMembership(user=self.user1, hoa_group=self.hoa_group, role='invalid_role')

        with self.assertRaises(ValidationError):
            membership.full_clean()
        self._notify_success("Role validation: Confirmed that role field only accepts 'admin' or 'member'")

    def test_membership_select_related_optimization(self):
        """Test that select_related works correctly for membership queries"""
        HOAMembership.objects.create(user=self.user1, hoa_group=self.hoa_group, role='member')

        # This should not raise any errors and should return the membership with related objects
        membership = HOAMembership.objects.select_related('user', 'hoa_group').first()

        self.assertEqual(membership.user.email, self.user1.email)
        self.assertEqual(membership.hoa_group.name, self.hoa_group.name)
        self._notify_success("Query optimization: Verified select_related works correctly with membership queries")

