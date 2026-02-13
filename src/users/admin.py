from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, Skill
from django.utils.html import format_html
from courses.models import Course


class CustomUserChangeForm(UserChangeForm):
    """Custom form with clearer labels for user types."""

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'is_staff' in self.fields:
            self.fields['is_staff'].label = 'Admin (can access admin portal)'
            self.fields['is_staff'].help_text = (
                'Admins can log into this admin site. '
                'Any user type (admin, professor, or student) can be an admin.'
            )
        if 'professor' in self.fields:
            self.fields['professor'].label = 'Professor'
            self.fields['professor'].help_text = (
                'Professors can create courses, review applications, and make offers. '
                'Uncheck for students.'
            )
        if 'is_superuser' in self.fields:
            self.fields['is_superuser'].help_text = (
                'Superusers have full permissions across the entire site. '
                'Can be combined with any user type.'
            )


def user_type_display(obj):
    """Display user type: Admin, Professor, or Student."""
    parts = []
    if obj.is_staff:
        parts.append('Admin')
    if obj.professor:
        parts.append('Professor')
    else:
        parts.append('Student')
    return ', '.join(parts)


user_type_display.short_description = 'User type'


def ta_status_display(obj):
    """Display TA status and which courses they're TA for."""
    if obj.course_working_for.exists():
        courses = obj.course_working_for.all()[:3]
        names = ', '.join(str(c) for c in courses)
        more = obj.course_working_for.count() - 3
        if more > 0:
            names += f' (+{more} more)'
        return format_html('<span style="color: green;">✓ TA</span> — {}', names)
    return format_html('<span style="color: #999;">—</span>')


ta_status_display.short_description = 'TA status'


class CourseTAInline(admin.TabularInline):
    """Inline to assign courses this user is a TA for."""
    model = Course.current_tas.through
    fk_name = 'customuser'
    extra = 0
    verbose_name = 'TA assignment'
    verbose_name_plural = 'TA assignments (courses this user TAs for)'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserChangeForm

    list_display = (
        'email', 'first_name', 'last_name', 'eagleid',
        user_type_display, 'is_superuser', ta_status_display
    )
    list_filter = ('is_staff', 'is_superuser', 'professor', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'eagleid')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'eagleid')}),
        (
            'User type',
            {
                'fields': ('is_staff', 'professor', 'is_superuser'),
                'description': (
                    'Admin = can access admin portal. Professor = teaches courses. '
                    'Student = applies for TAships (uncheck Professor). '
                    'Superuser = full permissions (any type can be superuser).'
                ),
            },
        ),
        ('Status', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'eagleid'),
            },
        ),
    )
    inlines = [CourseTAInline]


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
