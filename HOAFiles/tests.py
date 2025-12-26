from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from HOAFiles.models import User, HOAGroup, House
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

