from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, CourseEnrollment,Class_video, Semsiter_Even_odd,Website_logo, Slider_model
from .serializers import CourseSerializer
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import UserSession
import datetime
from django.contrib.sessions.models import Session
from django_user_agents.utils import get_user_agent
from django.utils.timezone import now
from .models import UserSession, LoginLog 

# Create your views here.

def home(request):
    course = Course.objects.all()[:3]
    print(course)
    slider = Slider_model.objects.all()
    print(slider)
    return render(request, 'index.html', {'slider': slider, 'courses': course})

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Course, CourseEnrollment, Class_video

def course_detail(request, id):
    today = timezone.now()
    enrolled = False

    if request.user.is_authenticated:
        user = request.user
        val = CourseEnrollment.objects.filter(user=user, course__id=id).first()
        
        if val is None:
            enrolled = False
        else:
            print(f"Today: {today}")
            print(f"Expired on: {val.expired_on}")
            if val.expired_on >= today:
                enrolled = True
            else:
                val.is_active = False
                val.save()
                enrolled = False

    course = get_object_or_404(Course, id=id)
    video = Class_video.objects.filter(course=course)

    return render(request, 'course-details.html', {
        'course': course,
        'enrolled': enrolled,
        'video': video
    })

def dashboard(request):
    return render(request, 'dashboard.html')

def course(request,data=None):
    if data is None:
        all = Course.objects.all()
    else:
        all = Course.objects.filter(semister=str(data))
    Even_odd = Semsiter_Even_odd.objects.all().first()
    return render(request, 'courses.html', {'all': all,"data":data, 'Even_odd': Even_odd})



def about(request):
    return render(request, 'about-us.html')

def footer(request):
    return render(request, 'footer.html')

class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not full_name or not email or not password or not confirm_password:
            return render(request, 'register.html', {'error': 'All fields are required.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken.'})
        
        if len(password) < 8:
            return render(request, 'register.html', {'error': 'Password must be at least 8 characters long.'})
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered.'})

        user = User(username=username, first_name=full_name, email=email)
        user.set_password(password)
        user.save()

        return render(request, 'register.html', {'success': 'Registration successful.'})

class Login_view(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {'error': 'Username and password are required.'})

        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()

        if user is None or not user.check_password(password):
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

        try:
            user_session = UserSession.objects.get(user=user)
            session_exists = Session.objects.filter(session_key=user_session.session_key).exists()

            if session_exists:
                return render(request, 'login.html', {'error': 'Already logged in on another device.'})
            else:
                login(request, user)
                user_session.session_key = request.session.session_key
                user_session.save()
        except UserSession.DoesNotExist:
            login(request, user)
            UserSession.objects.create(user=user, session_key=request.session.session_key)

        # Track device and log info
        user_agent = get_user_agent(request)
        device_type = 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'PC'
        os = user_agent.os.family
        browser = user_agent.browser.family
        ip = self.get_client_ip(request)

        # Optional: Save to LoginLog
        LoginLog.objects.create(
            user=user,
            ip_address=ip,
            device_type=device_type,
            os=os,
            browser=browser,
        )

        return redirect('home')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
def custom_logout(request):
    logout(request)
    return redirect('login')

class CourseListAPIView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
    
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import (
    Course, PaymentTransaction, PaymentVerification, 
    CourseEnrollment, PaymentMethod
)

@login_required
def student_payment_submit(request, course_id):
    """Student submits payment information"""
    course = get_object_or_404(Course, id=course_id)
    
    if CourseEnrollment.objects.filter(
        user=request.user, 
        course=course, 
        is_active=True,
        expired_on__gte=timezone.now()  # Changed from __gt to __gte
    ).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        sender_number = request.POST.get('sender_number')
        transaction_id = request.POST.get('transaction_id')
        
        if not all([amount, payment_method, sender_number, transaction_id]):
            messages.error(request, 'All fields are required!')
            return redirect('student_payment_submit', course_id=course_id)
        
        try:
            with transaction.atomic():
                payment = PaymentTransaction(
                    user=request.user,
                    course=course,
                    amount=amount,
                    payment_method=payment_method,
                    sender_number=sender_number,
                    transaction_id=transaction_id,
                    status='pending'
                )
                payment.reference_code = f"STU{timezone.now().strftime('%Y%m%d%H%M%S')}{request.user.id}"
                payment.save()
                
                messages.success(request, f'✅ Payment submitted! Reference: {payment.reference_code}')
                messages.info(request, 'Waiting for admin verification.')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('payment_status')
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    course_price = course.discounted_price if course.discounted_price else course.price
    
    context = {
        'course': course,
        'course_price': course_price,
        'payment_methods': payment_methods,
    }
    return render(request, 'student_payment_submit.html', context)

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_payment_verify(request):
    """Admin verifies payment by entering method, tr_id, amount"""
    
    pending_student_payments = PaymentTransaction.objects.filter(
        status='pending'
    ).order_by('-submitted_at')
    
    verified_payments = PaymentTransaction.objects.filter(
        status='verified'
    ).order_by('-verified_at')[:20]
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        amount = request.POST.get('amount')
        
        if not all([payment_method, transaction_id, amount]):
            messages.error(request, 'All fields are required!')
            return redirect('admin_payment_verify')
        
        try:
            with transaction.atomic():
                student_payment = PaymentTransaction.objects.filter(
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    amount=amount,
                    status='pending'
                ).first()
                
                if student_payment:
                    student_payment.status = 'verified'
                    student_payment.verified_at = timezone.now()
                    student_payment.save()
                    
                    PaymentVerification.objects.create(
                        user=student_payment.user,
                        reference_code=student_payment.reference_code,
                        transaction_id=transaction_id,
                        sender_number=student_payment.sender_number,
                        payment_method=payment_method,
                        amount=amount,
                        is_verified=True,
                        matched_transaction=student_payment
                    )
                    
                    enroll_student_in_course(student_payment.user, student_payment.course)
                    
                    messages.success(request, f'✅ MATCH FOUND! {student_payment.user.username} enrolled in {student_payment.course.name}!')
                else:
                    messages.error(request, '❌ No matching student submission found!')
                    
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('admin_payment_verify')
    
    total_pending = pending_student_payments.count()
    total_verified_today = PaymentTransaction.objects.filter(
        status='verified',
        verified_at__date=timezone.now().date()
    ).count()
    
    total_revenue = PaymentTransaction.objects.filter(
        status='verified'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'payment_methods': payment_methods,
        'pending_student_payments': pending_student_payments,
        'verified_payments': verified_payments,
        'total_pending': total_pending,
        'total_verified_today': total_verified_today,
        'total_revenue': total_revenue,
    }
    return render(request, 'admin_payment_verify.html', context)
def enroll_student_in_course(user, course):
    """Enroll user in course using course end date"""
    # Get or create enrollment
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            'expired_on': timezone.make_aware(datetime.combine(course.end_date, datetime.max.time())),
            'is_active': True
        }
    )
    
    print(enrollment.expired_on,"hi")
    print(course.end_date,"hello")
    
    if not created:
        # Update existing enrollment
        enrollment.is_active = True
        enrollment.enrolled_on = timezone.now()
        enrollment.expired_on = timezone.make_aware(datetime.combine(course.end_date, datetime.max.time()))
        enrollment.save()


@login_required
def payment_status(request):
    """Student views payment status"""
    payments = PaymentTransaction.objects.filter(
        user=request.user
    ).order_by('-submitted_at')
    
    # Use __gte to include enrollments that expire today
    active_enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        is_active=True,
        expired_on__gte=timezone.now()  # Changed from __gt to __gte
    )
    
    context = {
        'payments': payments,
        'active_enrollments': active_enrollments,
    }
    return render(request, 'payment_status.html', context)

@login_required
def course_access_check(request, course_id):
    """Check if user has access to course"""
    course = get_object_or_404(Course, id=course_id)
    
    enrollment = CourseEnrollment.objects.filter(
        user=request.user,
        course=course,
        is_active=True,
        expired_on__gte=timezone.now()  # Changed from __gt to __gte
    ).first()
    
    if enrollment:
        return render(request, 'course_content.html', {
            'course': course, 
            'enrollment': enrollment
        })
    else:
        messages.warning(request, 'You do not have access to this course. Please enroll first.')
        return redirect('course_detail', course_id=course.id)