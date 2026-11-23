from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'deadline', 'created_by', 'submission_count')
    list_filter = ('language',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
