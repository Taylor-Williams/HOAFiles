from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, HOAGroup, House, Document, HOAMembership


@csrf_exempt
def login_page(request):
    """Render the login/registration page"""
    if request.method == 'GET':
        return render(request, 'HOAFiles/login.html')
    return render(request, 'HOAFiles/login.html')


@csrf_exempt
def register_user(request):
    """Register a new user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=400)
            
            user = User.objects.create(email=email)
            user.set_password(password)
            user.save()
            
            return JsonResponse({
                'id': user.id,
                'email': user.email,
                'message': 'User created successfully'
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def login_user(request):
    """Login a user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return JsonResponse({
                        'id': user.id,
                        'email': user.email,
                        'message': 'Login successful'
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def user_hoa_groups(request, user_id):
    """Get or create HOAGroups for a user"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    if request.method == 'GET':
        hoa_groups = HOAGroup.objects.filter(users=user)
        return JsonResponse({
            'user_id': user.id,
            'hoa_groups': [{
                'id': hg.id,
                'name': hg.name,
                'owner_email': hg.owner_email,
                'role': hg.get_user_role(user)
            } for hg in hoa_groups]
        }, status=200)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            owner_email = data.get('owner_email')
            
            if not name or not owner_email:
                return JsonResponse({'error': 'Name and owner_email are required'}, status=400)

            if HOAGroup.objects.filter(name=name).exists():
                return JsonResponse({'error': 'HOAGroup with this name already exists'}, status=400)

            if HOAGroup.objects.filter(owner_email=owner_email).exists():
                return JsonResponse({'error': 'HOAGroup with this owner_email already exists'}, status=400)
            
            hoa_group = HOAGroup.objects.create(name=name, owner_email=owner_email)
            # Create membership with admin role for the creator
            HOAMembership.objects.create(user=user, hoa_group=hoa_group, role='admin')

            return JsonResponse({
                'id': hoa_group.id,
                'name': hoa_group.name,
                'owner_email': hoa_group.owner_email,
                'role': 'admin',
                'message': 'HOAGroup created successfully'
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def user_houses(request, user_id):
    """Get or create Houses for a user"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    if request.method == 'GET':
        houses = House.objects.filter(users=user)
        return JsonResponse({
            'user_id': user.id,
            'houses': [{
                'id': h.id,
                'address': h.address
            } for h in houses]
        }, status=200)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            address = data.get('address')
            
            if not address:
                return JsonResponse({'error': 'Address is required'}, status=400)
            
            if House.objects.filter(address=address).exists():
                return JsonResponse({'error': 'House with this address already exists'}, status=400)
            
            house = House.objects.create(address=address)
            house.users.add(user)
            
            return JsonResponse({
                'id': house.id,
                'address': house.address,
                'message': 'House created successfully'
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def user_dashboard(request, user_id):
    """Display user dashboard with HOA groups and houses"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("User not found")

    # Get user's HOA groups with role information
    memberships = user.hoa_memberships.select_related('hoa_group').all()
    hoa_groups_with_roles = [{
        'id': m.hoa_group.id,
        'name': m.hoa_group.name,
        'owner_email': m.hoa_group.owner_email,
        'role': m.role
    } for m in memberships]

    houses = user.houses.all()

    context = {
        'user': user,
        'hoa_groups': hoa_groups_with_roles,
        'houses': houses,
    }

    return render(request, 'HOAFiles/dashboard.html', context)


@csrf_exempt
def search_hoa_groups(request, user_id):
    """Search for HOAGroups by name that the user can join"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({'hoa_groups': []}, status=200)

        # Search for HOAGroups by name, excluding ones user already belongs to
        user_hoa_ids = user.hoa_groups.values_list('id', flat=True)
        hoa_groups = HOAGroup.objects.filter(name__icontains=query).exclude(id__in=user_hoa_ids)[:10]

        return JsonResponse({
            'hoa_groups': [{
                'id': hg.id,
                'name': hg.name,
                'owner_email': hg.owner_email
            } for hg in hoa_groups]
        }, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def join_hoa_group(request, user_id, hoa_group_id):
    """Add a user to an existing HOAGroup"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    try:
        hoa_group = HOAGroup.objects.get(pk=hoa_group_id)
    except HOAGroup.DoesNotExist:
        return JsonResponse({'error': 'HOAGroup not found'}, status=404)

    if request.method == 'POST':
        # Check if user is already a member
        if HOAMembership.objects.filter(user=user, hoa_group=hoa_group).exists():
            return JsonResponse({'error': 'User is already a member of this HOAGroup'}, status=400)

        # Create membership with member role
        HOAMembership.objects.create(user=user, hoa_group=hoa_group, role='member')

        return JsonResponse({
            'id': hoa_group.id,
            'name': hoa_group.name,
            'owner_email': hoa_group.owner_email,
            'role': 'member',
            'message': 'Successfully joined HOAGroup'
        }, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def hoa_group_dashboard(request, hoa_group_id):
    """Display HOA group dashboard with documents and members"""
    try:
        hoa_group = HOAGroup.objects.get(pk=hoa_group_id)
    except HOAGroup.DoesNotExist:
        from django.http import Http404
        raise Http404("HOA Group not found")

    # Get current user from query param
    user_id = request.GET.get('user_id')
    current_user = None
    is_admin = False

    if user_id:
        try:
            current_user = User.objects.get(pk=user_id)
            is_admin = hoa_group.is_admin(current_user)
        except User.DoesNotExist:
            pass

    documents = hoa_group.documents.all().order_by('-created_at')
    # Get members with their roles
    memberships = hoa_group.memberships.select_related('user').all()

    context = {
        'hoa_group': hoa_group,
        'documents': documents,
        'memberships': memberships,
        'is_admin': is_admin,
        'current_user': current_user,
    }

    return render(request, 'HOAFiles/hoa_dashboard.html', context)


@csrf_exempt
def hoa_group_documents(request, hoa_group_id):
    """Get or create documents for an HOA group"""
    try:
        hoa_group = HOAGroup.objects.get(pk=hoa_group_id)
    except HOAGroup.DoesNotExist:
        return JsonResponse({'error': 'HOA Group not found'}, status=404)

    if request.method == 'GET':
        documents = hoa_group.documents.all().order_by('-created_at')
        return JsonResponse({
            'hoa_group_id': hoa_group.id,
            'documents': [{
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat()
            } for doc in documents]
        }, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content', '')
            user_id = data.get('user_id')

            # Permission check: only admins can create documents
            if not user_id:
                return JsonResponse({'error': 'User ID required'}, status=400)

            try:
                user = User.objects.get(pk=user_id)
                if not hoa_group.is_admin(user):
                    return JsonResponse({'error': 'Only admins can create documents'}, status=403)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)

            document = Document.objects.create(
                title=title,
                content=content,
                hoa_group=hoa_group
            )

            return JsonResponse({
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat(),
                'message': 'Document created successfully'
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_document(request, hoa_group_id, document_id):
    """Delete or update a document from an HOA group"""
    try:
        hoa_group = HOAGroup.objects.get(pk=hoa_group_id)
    except HOAGroup.DoesNotExist:
        return JsonResponse({'error': 'HOA Group not found'}, status=404)

    try:
        document = Document.objects.get(pk=document_id, hoa_group=hoa_group)
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)

    if request.method == 'DELETE':
        # Permission check: only admins can delete documents
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User ID required'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
            if not hoa_group.is_admin(user):
                return JsonResponse({'error': 'Only admins can delete documents'}, status=403)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        document.delete()
        return JsonResponse({'message': 'Document deleted successfully'}, status=200)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content', '')
            user_id = data.get('user_id')

            # Permission check: only admins can update documents
            if not user_id:
                return JsonResponse({'error': 'User ID required'}, status=400)

            try:
                user = User.objects.get(pk=user_id)
                if not hoa_group.is_admin(user):
                    return JsonResponse({'error': 'Only admins can update documents'}, status=403)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)

            document.title = title
            document.content = content
            document.save()

            return JsonResponse({
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat(),
                'message': 'Document updated successfully'
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

