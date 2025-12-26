from django.contrib import admin
from .models import User, HOAGroup, House, Document, HOAMembership


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('email',)


class HOAMembershipInline(admin.TabularInline):
    model = HOAMembership
    extra = 1


@admin.register(HOAGroup)
class HOAGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner_email')
    search_fields = ('name', 'owner_email')
    inlines = [HOAMembershipInline]


@admin.register(HOAMembership)
class HOAMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'hoa_group', 'role', 'joined_at')
    list_filter = ('role', 'hoa_group')
    search_fields = ('user__email', 'hoa_group__name')


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'address')
    search_fields = ('address',)
    filter_horizontal = ('users',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'hoa_group', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('hoa_group',)
