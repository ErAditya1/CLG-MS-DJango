
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator
# Create your models here.

def avatar_upload_path(instance, filename):
    return f'avatars/{instance.username}/{filename}'
class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('guest', 'Guest'),
    )


    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='guest')
    email = models.EmailField(max_length=254,unique=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_detailed = models.BooleanField(default=False)

    # Fixing the clashes with related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Change related_name here
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Change related_name here
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
   

    def __str__(self):
        return self.username

class SchoolClass(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Class 10", "Class 12"

    def __str__(self):
        return self.name

class Section(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=50)  # e.g., "A", "B", "C"

    class Meta:
        unique_together = ('school_class', 'name')

    def __str__(self):
        return f"{self.school_class.name} - {self.name}"
    
class FeesType(models.Model):
    
    name = models.CharField(max_length=100)  # eg: Tuition Fee, Exam Fee
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='fees_types')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='fees_types', null=True)

    def __str__(self):
        return f" {self.name}"



class Entrance(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField()


    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    name = models.CharField(max_length=100)


    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)


    subject_code = models.CharField(max_length=50, null=True, unique=True)
    def __str__(self):
        return self.name
class Student(models.Model):
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    FEE_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
    )

    ADMISSION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User , on_delete=models.CASCADE,  related_name='student' )
    rollno = models.CharField(unique=True, max_length=20)
    
    # form 1

    date_of_birth = models.DateField(null=True, blank=True)
    fname = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    gender = models.CharField(max_length=6, choices= GENDER)
    aadhar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='student_images', null=True, blank=True)
    aadhar_imag = models.FileField(upload_to='aadhar_images', null=True, blank=True)
    # email = models.EmailField( max_length=254)
    



    # form 2>> 🏡 Contact Information
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    #  form 3>> 🎓 Academic Details
    previous_school = models.CharField(max_length=255, null=True)
    last_qualification = models.CharField(max_length=100, null= True)
    year_of_passing = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=20, null=True)

    #  📚 Admission Info
   
    entrance_exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_eligible_for_admission = models.BooleanField(default=False)
    admission_status = models.CharField(max_length=10, choices=ADMISSION_STATUS_CHOICES, default='pending')
    admission_date = models.DateField(auto_now_add=True, null=True, blank=True)
   

    # 💳 Fee / Payment Info

    payment_method = models.CharField(max_length=50, blank=True, null=True)
    scholarship_status = models.BooleanField(default=False)


    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)


    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, related_name='students')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, related_name='students')





    def __str__(self):
        return self.user.username

class StudentFee(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('UPI', 'UPI'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_fees')
    fee_type = models.ForeignKey(FeesType, on_delete=models.CASCADE, related_name='student_fees')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50,choices=PAYMENT_METHODS,null=True)  # e.g., UPI, Card, Bank Transfer
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    receipt_id = models.CharField(max_length=100, unique=True, null=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='student_fee_paid_by')

    def __str__(self):
        return f"{self.student.rollno} - {self.fee_type.name} - ₹{self.amount_paid}"
    def save(self, *args, **kwargs):
        if not self.receipt_id:
            self.receipt_id = self.generate_receipt_id()
        super().save(*args, **kwargs)

    def generate_receipt_id(self):
        prefix = 'RCPT'
        unique_code = get_random_string(length=6).upper()
        return f"{prefix}-{self.student.rollno}-{unique_code}"

class Employee(models.Model):
    """Represents a school staff member (teacher/admin/etc.)."""
    EMPLOYEE_TYPES = [
        ('teacher', 'Teacher'),
        ('admin',   'Admin'),
        ('staff',   'Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
    date_joined = models.DateField(auto_now_add=True)
    # Add other fields (department, designation) as needed.

    def __str__(self):
        return f"{self.user.get_full_name} ({self.get_role_display()})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')

    # Personal Info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10,null=True, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])

    aadhar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='student_images', null=True, blank=True)
    aadhar_imag = models.FileField(upload_to='aadhar_images', null=True, blank=True)
    qualification_doc = models.FileField(upload_to='qualification_docs', null=True, blank=True)
    # Academic Info
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True,null=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)

        # form 2>> 🏡 Contact Information
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # System Info
    join_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class TeacherInterest(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="interests")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="interested_teachers")


    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)



    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.name} ({self.school_class.name}/{self.section.name})"



class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='admin')
    employee_id = models.CharField(max_length=20)
    office = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
 
class StudyMaterial(models.Model):               # upload study material
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_materials')


    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)




    subject = models.CharField( max_length=500)
    file_name = models.CharField( max_length=200)
    file = models.FileField(upload_to='myimage')
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject

class Assesment(models.Model):  #Upload Asignment
    user = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name='assesments')

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)




    subject = models.CharField( max_length=500)
    file_name = models.CharField( max_length=200)
    file = models.FileField(upload_to='myimage')
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject


class Lecture(models.Model):  # Upload Lectures
    user = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name='lectures')

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)



    subject = models.CharField( max_length=50)
    file_name = models.CharField( max_length=200)
    link = models.URLField( max_length=500)
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): 
        return self.subject

class Complaint(models.Model):
    student = models.ForeignKey(Student,null = True, on_delete=models.CASCADE, related_name='complaints')
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_complaints')
    # admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_complaints')
    subject = models.CharField(max_length=200)
    comp = models.TextField(max_length = 1000)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject

class Feedback(models.Model):
    student = models.ForeignKey(Student,null = True, on_delete=models.CASCADE, related_name='feedbacks')
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_feedback')
    # admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_feedback')
    subject = models.CharField(max_length=200)
    feed = models.TextField(max_length = 1000)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject

class Enquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ENQUIRY',null=True)
    name = models.CharField( max_length=50)
    gender = models.CharField( max_length=50)
    address = models.CharField( max_length=300)
    mobile = models.CharField( max_length=15)
    email = models.EmailField( max_length=254)
    text = models.CharField( max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='notifications', null=True)
    text = models.CharField(max_length=500)
    link = models.URLField ( max_length=350)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Gallery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='gallery_images')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Gallery Image {self.id}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)  # True for present, False for absent

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)


    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='attendance', null=True)  # Teacher or Admin who submitted the attendance
    

    def __str__(self):
        return f"{self.student.user.username} - {self.date} - {'Present' if self.status else 'Absent'}"
    
class DayChoices(models.TextChoices):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    # SUNDAY = 'Sunday'

class Period(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Period 1", "Period 2"
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class TimetableEntry(models.Model):
    day = models.CharField(max_length=10, choices=DayChoices.choices)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('day', 'period', 'school_class', 'section')

    def __str__(self):
        return f"{self.day} - {self.period.name} - {self.subject} ({self.school_class.name}-{self.section.name})"


class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    view_name = models.CharField(max_length=255)
    error_type = models.CharField(max_length=255)
    error_message = models.TextField()
    stack_trace = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SalaryStructure(models.Model):
    """Salary components for an employee (one structure per employee)."""
    employee = models.OneToOneField(Employee, on_delete=models.PROTECT)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total
        self.total_salary = (
            self.base_salary + self.bonuses + self.allowances - self.deductions - self.tax_percent
        )
        super().save(*args, **kwargs)

class EmployeeAttendance(models.Model):
    """Daily attendance record for integration with payroll."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent',  'Absent'),
        ('halfday', 'Half Day'),
        # Add other statuses if needed.
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date     = models.DateTimeField(auto_now_add=True)
    status   = models.CharField(max_length=10, choices=STATUS_CHOICES)
    # submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    
    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.user.get_full_name} - {self.date}: {self.get_status_display()}"

class SalaryPayment(models.Model):
    """A monthly salary payout record (with breakdown)."""
    employee         = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.PROTECT)
    date             = models.DateField(help_text="Payment date")
    worked_days      = models.IntegerField(default=0)
    absent_days      = models.IntegerField(default=0)
    # Copy salary components (snapshot for this payment)
    base_salary      = models.DecimalField(max_digits=10, decimal_places=2)
    allowances       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent      = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    net_salary       = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def calculate_net(self):
        """Calculate net salary based on attendance and components."""
        # Example logic: pro-rate basic by attendance and apply tax.
        total_days = self.worked_days + self.absent_days or 1
        per_day = self.base_salary / total_days
        earned_basic = per_day * self.worked_days
        gross = earned_basic + self.allowances + self.bonuses
        tax_amount = gross * (self.tax_percent / 100)
        self.net_salary = gross - (self.deductions + tax_amount)
        return self.net_salary

    def save(self, *args, **kwargs):
        # On first save, copy the structure’s values
        if not self.id:
            self.base_salary      = self.salary_structure.base_salary
            self.allowances = self.salary_structure.allowances
            self.bonuses    = self.salary_structure.bonuses
            self.deductions = self.salary_structure.deductions
            self.tax_percent= self.salary_structure.tax_percent
        # Recalculate net salary on every save
        self.calculate_net()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payout for {self.employee.user.get_full_name} on {self.date}"

class Payslip(models.Model):
    """Generated payslip document for a salary payment."""
    salary_payment = models.OneToOneField(SalaryPayment, on_delete=models.CASCADE)
    generated_on   = models.DateTimeField(auto_now_add=True)
    file           = models.FileField(upload_to='payslips/')

    def __str__(self):
        return f"Payslip for {self.salary_payment.employee.user.get_full_name} ({self.salary_payment.date})"


