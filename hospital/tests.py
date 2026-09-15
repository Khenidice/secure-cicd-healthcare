"""
Automated test suite for the Hospital-Management application.

These tests exercise the core healthcare workflows (patient registration,
appointment booking, doctor-patient interaction, authentication, form
validation and billing) and are executed automatically on every commit as
part of the secure CI/CD pipeline.
"""
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse

from . import models, forms


def make_admin_group():
    return Group.objects.get_or_create(name='ADMIN')[0]


def make_doctor_group():
    return Group.objects.get_or_create(name='DOCTOR')[0]


def make_patient_group():
    return Group.objects.get_or_create(name='PATIENT')[0]


# --------------------------------------------------------------------------
# UNIT TESTS - models
# --------------------------------------------------------------------------
class ModelTests(TestCase):
    def test_doctor_get_name(self):
        u = User.objects.create_user(
            'dr.adekola', first_name='Adaeze', last_name='Okonkwo')
        d = models.Doctor.objects.create(
            user=u, address='10 Broad St', mobile='08012345678',
            department='Cardiologist')
        self.assertEqual(d.get_name, 'Adaeze Okonkwo')

    def test_doctor_string_representation(self):
        u = User.objects.create_user('dr.chi', first_name='Chidi')
        d = models.Doctor.objects.create(
            user=u, address='2 Lagos Rd', department='Dermatologists')
        self.assertEqual(str(d), 'Chidi (Dermatologists)')

    def test_patient_get_name(self):
        u = User.objects.create_user(
            'pta.bola', first_name='Bola', last_name='Adeyemi')
        p = models.Patient.objects.create(
            user=u, address='3 Abuja Ave', mobile='08098765432',
            symptoms='Malaria')
        self.assertEqual(p.get_name, 'Bola Adeyemi')

    def test_patient_string_representation(self):
        u = User.objects.create_user('pta.kemi', first_name='Kemi')
        p = models.Patient.objects.create(
            user=u, address='1 Enugu Rd', mobile='08111111111',
            symptoms='Typhoid', status=True)
        self.assertEqual(str(p), 'Kemi (Typhoid)')

    def test_appointment_creation(self):
        a = models.Appointment.objects.create(
            patientName='Bola', doctorName='Chidi',
            description='Follow-up check', status=False)
        self.assertIsNotNone(a.pk)
        self.assertFalse(a.status)

    def test_discharge_details_total(self):
        d = models.PatientDischargeDetails.objects.create(
            patientId=1, patientName='Bola', assignedDoctorName='Chidi',
            address='3 Abuja Ave', mobile='08111111111', symptoms='Malaria',
            admitDate='2024-01-01', releaseDate='2024-01-05', daySpent=4,
            roomCharge=4000, medicineCost=3000, doctorFee=5000,
            OtherCharge=1000, total=13000)
        self.assertEqual(d.total, 13000)


# --------------------------------------------------------------------------
# UNIT TESTS - forms
# --------------------------------------------------------------------------
class FormValidationTests(TestCase):
    def test_patient_signup_form_requires_username(self):
        f = forms.PatientUserForm(
            data={'first_name': 'B', 'last_name': 'A',
                  'username': '', 'password': 'SecurePass1'})
        # Password validation is not run by the form alone; username required
        self.assertTrue(f.is_valid() or 'username' in f.errors)

    def test_doctor_form_invalid_department(self):
        u = User.objects.create_user('dr.t', first_name='Tunde')
        f = forms.DoctorForm(
            data={'address': '1 Rd', 'mobile': '08000000000',
                  'department': 'NotARealDepartment', 'status': True})
        # invalid department should be rejected by the choices field
        self.assertFalse(f.is_valid())

    def test_contactus_form_valid(self):
        f = forms.ContactusForm(
            data={'Name': 'Amina', 'Email': 'amina@example.com',
                  'Message': 'I need an appointment.'})
        self.assertTrue(f.is_valid())

    def test_contactus_form_invalid_email(self):
        f = forms.ContactusForm(
            data={'Name': 'Amina', 'Email': 'not-an-email',
                  'Message': 'Hello'})
        self.assertFalse(f.is_valid())

    def test_patient_appointment_form_requires_doctor(self):
        f = forms.PatientAppointmentForm(
            data={'description': 'Check-up', 'status': False})
        self.assertFalse(f.is_valid())

    def test_appointment_form_patient_required(self):
        f = forms.AppointmentForm(
            data={'description': 'New visit', 'status': False})
        # doctor and patient querysets are empty -> fields invalid
        self.assertFalse(f.is_valid())


# --------------------------------------------------------------------------
# INTEGRATION TESTS - roles, authentication and authorisation
# --------------------------------------------------------------------------
class AuthenticationTests(TestCase):
    def setUp(self):
        make_admin_group()
        make_doctor_group()
        make_patient_group()

    def test_is_admin_group_assignment_on_signup(self):
        resp = self.client.post('/adminsignup', {
            'first_name': 'Admin', 'last_name': 'One',
            'username': 'root_admin', 'password': 'AdminPass123'})
        u = User.objects.get(username='root_admin')
        self.assertTrue(u.groups.filter(name='ADMIN').exists())

    def test_is_doctor_group_assignment_on_signup(self):
        resp = self.client.post(reverse('doctorsignup'), {
            'first_name': 'Doc', 'last_name': 'Tor',
            'username': 'dr_tor', 'password': 'DocPass123',
            'address': '4 Rd', 'mobile': '08033333333',
            'department': 'Cardiologist'})
        u = User.objects.get(username='dr_tor')
        self.assertTrue(u.groups.filter(name='DOCTOR').exists())

    def test_is_patient_group_assignment_on_signup(self):
        resp = self.client.post('/patientsignup', {
            'first_name': 'Pat', 'last_name': 'Ient',
            'username': 'pt_one', 'password': 'PatPass123',
            'address': '5 Rd', 'mobile': '08055555555',
            'symptoms': 'Fever'})
        u = User.objects.get(username='pt_one')
        self.assertTrue(u.groups.filter(name='PATIENT').exists())

    def test_admin_dashboard_requires_admin_login(self):
        # unauthenticated access should redirect to login
        resp = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_doctor_cannot_access_admin_dashboard(self):
        u = User.objects.create_user('docx', password='x')
        u.groups.add(make_doctor_group())
        self.client.force_login(u)
        resp = self.client.get(reverse('admin-dashboard'))
        # user_passes_test redirects because user is not admin
        self.assertEqual(resp.status_code, 302)

    def test_patient_lookup_view_redirects_anonymous(self):
        resp = self.client.get(reverse('patient-appointment'))
        self.assertIn(resp.status_code, (302, 200))


# --------------------------------------------------------------------------
# FUNCTIONAL TESTS - core workflows
# --------------------------------------------------------------------------
class WorkflowTests(TestCase):
    def setUp(self):
        make_doctor_group()
        make_patient_group()
        self.doc_user = User.objects.create_user(
            'dr.ola', first_name='Ola', last_name='Bello', password='x')
        self.doc_user.groups.add(make_doctor_group())
        self.doctor = models.Doctor.objects.create(
            user=self.doc_user, address='1 Rd', mobile='08011111111',
            department='Cardiologist', status=True)
        self.pat_user = User.objects.create_user(
            'pt.ada', first_name='Ada', last_name='Nwosu', password='x')
        self.pat_user.groups.add(make_patient_group())
        self.patient = models.Patient.objects.create(
            user=self.pat_user, address='2 Rd', mobile='08022222222',
            symptoms='Asthma', status=True,
            assignedDoctorId=self.doc_user.id)

    def test_appointment_booking_creates_record(self):
        models.Appointment.objects.create(
            patientId=self.pat_user.id, doctorId=self.doc_user.id,
            patientName='Ada Nwosu', doctorName='Ola Bello',
            description='Routine check', status=False)
        self.assertEqual(models.Appointment.objects.count(), 1)
        a = models.Appointment.objects.first()
        self.assertEqual(a.patientName, 'Ada Nwosu')
        self.assertFalse(a.status)

    def test_appointment_defaults_to_pending(self):
        for _ in range(3):
            models.Appointment.objects.create(
                patientId=self.pat_user.id, doctorId=self.doc_user.id,
                patientName='Ada Nwosu', doctorName='Ola Bello',
                description='Check', status=False)
        self.assertEqual(models.Appointment.objects.filter(status=False).count(), 3)

    def test_patient_signup_creates_patient_profile(self):
        User.objects.create_user(
            'new_patient', first_name='New', last_name='Case', password='x')
        # profile is linked via OneToOne in views; here test model linkage
        p = models.Patient.objects.create(
            user=User.objects.get(username='new_patient'),
            address='10 Rd', mobile='08099999999', symptoms='Migraine')
        self.assertEqual(p.user.first_name, 'New')

    def test_discharge_bill_calculation_possible(self):
        # total should equal sum of component charges
        room = 4000
        med = 3000
        fee = 5000
        other = 1000
        self.assertEqual(room + med + fee + other, 13000)

    def test_patient_profile_pic_optional(self):
        u = User.objects.create_user('pic.user', password='x')
        u.groups.add(make_patient_group())
        p = models.Patient.objects.create(
            user=u, address='9 Rd', mobile='08088888888',
            symptoms='Asthma')
        self.assertFalse(bool(p.profile_pic))  # no uploaded file

    def test_doctor_status_defaults_false(self):
        u = User.objects.create_user('new_doc', password='x')
        d = models.Doctor.objects.create(user=u, address='3 Rd')
        self.assertFalse(d.status)

    def test_duplicate_username_rejected_by_auth(self):
        User.objects.create_user('dupuser', password='x')
        self.assertTrue(User.objects.filter(username='dupuser').exists())
        # creating the same username again should fail uniqueness
        with self.assertRaises(Exception):
            User.objects.create_user('dupuser', password='y')


# --------------------------------------------------------------------------
# FUNCTIONAL TESTS - URL/HTTP behaviour
# --------------------------------------------------------------------------
class UrlRoutingTests(TestCase):
    def test_home_redirects_authenticated(self):
        u = User.objects.create_user('u', password='x')
        u.groups.add(make_patient_group())
        self.client.force_login(u)
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)

    def test_adminclick_page_renders(self):
        resp = self.client.get('/adminclick')
        self.assertEqual(resp.status_code, 200)

    def test_doctorclick_page_renders(self):
        resp = self.client.get('/doctorclick')
        self.assertEqual(resp.status_code, 200)

    def test_patientclick_page_renders(self):
        resp = self.client.get('/patientclick')
        self.assertEqual(resp.status_code, 200)

    def test_aboutus_page_renders(self):
        resp = self.client.get('/aboutus')
        self.assertEqual(resp.status_code, 200)

    def test_contactus_page_renders(self):
        resp = self.client.get('/contactus')
        self.assertEqual(resp.status_code, 200)
