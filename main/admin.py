from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, Employee, Rating

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'service', 'created_at')
    list_filter = ('service', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'specialty', 'email', 'image_tag', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('name', 'role', 'specialty', 'description')
    readonly_fields = ('created_at', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: auto; object-fit: cover;" />', obj.image.url)
        return '-'
    image_tag.short_description = 'Photo'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'email', 'comment')
    readonly_fields = ('created_at',)
