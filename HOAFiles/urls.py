from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('dashboard/<int:user_id>/', views.user_dashboard, name='user_dashboard'),
    path('hoa-group/<int:hoa_group_id>/dashboard/', views.hoa_group_dashboard, name='hoa_group_dashboard'),
    path('api/users/register/', views.register_user, name='register_user'),
    path('api/users/login/', views.login_user, name='login_user'),
    path('api/users/<int:user_id>/hoa-groups/', views.user_hoa_groups, name='user_hoa_groups'),
    path('api/users/<int:user_id>/hoa-groups/search/', views.search_hoa_groups, name='search_hoa_groups'),
    path('api/users/<int:user_id>/hoa-groups/<int:hoa_group_id>/join/', views.join_hoa_group, name='join_hoa_group'),
    path('api/users/<int:user_id>/houses/', views.user_houses, name='user_houses'),
    path('api/hoa-groups/<int:hoa_group_id>/documents/', views.hoa_group_documents, name='hoa_group_documents'),
    path('api/hoa-groups/<int:hoa_group_id>/documents/<int:document_id>/', views.delete_document, name='delete_document'),
]


