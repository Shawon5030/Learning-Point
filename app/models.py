from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class CourseInstructor(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    institute = models.CharField(max_length=100)
    image = models.URLField(max_length=200,blank=True,null=True)

    def __str__(self):
        return self.name
    

semister_choice = (
    ('first-semester','first-semester'),
    ('second-semester','second-semester'),
    ('third-semester','third-semester'),
    ('fourth-semester','fourth-semester'),
    ('fifth-semester', 'fifth-semester'),
    ('sixth-semester','sixth-semester'),
    ('seventh-semester','seventh-semester'),
   
    
)

class Course(models.Model):
    name = models.CharField(max_length=100)
    picture = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField()
    start_date = models.DateField()
    price = models.IntegerField(default=0,null=True,blank=True)
    discount = models.IntegerField(default=0,null=True,blank=True)
    discounted_price = models.IntegerField(blank=True, null=True)
    end_date = models.DateField()
    enroll = models.BooleanField(default=False)
    semister = models.CharField(choices=semister_choice, max_length=20, blank=True, null=True)
    instructor = models.ForeignKey(CourseInstructor, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @property
    def duration_days(self):
        """Calculate course duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def is_active_course(self):
        """Check if course is currently active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    
even_odd_choice = (
    ('Even',"Even"),
    ('Odd',"Odd"),
)
class Semsiter_Even_odd(models.Model):
    even_odd = models.CharField(choices=even_odd_choice,blank=True,null=True,max_length=10)

    def __str__(self):
        return self.even_odd

class Website_logo(models.Model):
    image = models.URLField()
    
class Slider_model(models.Model):
    image = models.URLField()
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tag_line = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "Slider Image"
    
    
class Class_video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video_url = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "Class Video"
    
class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_on = models.DateTimeField(auto_now_add=True)
    expired_on = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expired_on
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if not self.is_expired:
            return (self.expired_on - timezone.now()).days
        return 0
    
    
class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    device_type = models.CharField(max_length=20)
    os = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    login_time = models.DateTimeField(auto_now_add=True)
    
    
# Payment Models

class PaymentMethod(models.Model):
    PAYMENT_CHOICES = (
        ('bkash', 'Bkash'),
        ('rocket', 'Rocket'),
        ('nagad', 'Nagad'),
    )
    name = models.CharField(max_length=20, choices=PAYMENT_CHOICES, unique=True)
    account_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()

class PaymentTransaction(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.PAYMENT_CHOICES)
    sender_number = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50, unique=True)
    reference_code = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_id}"

class PaymentVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    reference_code = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50)
    sender_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    matched_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.reference_code}"