from django.contrib import admin
from .models import LoginLog,Course,UserSession,CourseEnrollment, CourseInstructor,Class_video,Semsiter_Even_odd,Website_logo , Slider_model
# Register your models here.

admin.site.site_header = "Learn's Point Management Admin"
admin.site.site_title = "Course Management Admin Portal"
admin.site.index_title = "Welcome to Learn's Point Management Admin Portal"



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'start_date', 'end_date', 'enroll')
    search_fields = ('name', 'instructor__name')
    list_filter = ('start_date', 'end_date', 'enroll')
    ordering = ('start_date',)
    
@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'institute')
    search_fields = ('name', 'institute')
    ordering = ('name',)
    
# Registering models with the admin site
@admin.register(Semsiter_Even_odd)
class SemsiterEvenOddAdmin(admin.ModelAdmin):
    list_display = ('even_odd',)
    search_fields = ('even_odd',)
    ordering = ('even_odd',)
    
admin.site.register(Website_logo)

@admin.register(Slider_model)
class SliderModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag_line')
    search_fields = ('title', 'description')
    ordering = ('title',)
    

@admin.register(Class_video)
class ClassVideoAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'course','title')
    search_fields = ('name', 'course__name')
    
admin.site.register(UserSession)

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course','enrolled_on', 'expired_on', 'is_active')
    search_fields = ('user__username', 'course__name')
    list_filter = ('course',)
    ordering = ('user',)
    

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device_type', 'os','browser','login_time')
    search_fields = ('user__username',)
    list_filter = ('login_time',)
    
    
    
from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction, PaymentVerification

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_number', 'is_active']
    list_filter = ['is_active']
    search_fields = ['account_number']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'payment_method', 'transaction_id', 'status', 'submitted_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['transaction_id', 'reference_code', 'sender_number']
    readonly_fields = ['submitted_at']

@admin.register(PaymentVerification)
class PaymentVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'reference_code', 'transaction_id', 'amount', 'is_verified', 'submitted_at']
    list_filter = ['is_verified', 'payment_method']
    search_fields = ['reference_code', 'transaction_id', 'sender_number']