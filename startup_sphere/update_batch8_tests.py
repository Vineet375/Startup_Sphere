import os

file_path = 'incubator/tests.py'

new_tests = """
from .models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from decimal import Decimal

class Batch8InvestorTests(TestCase):
    def setUp(self):
        self.investor = User.objects.create_user(username='inv1', password='123', role='investor')
        self.investor_profile = InvestorProfile.objects.create(
            user=self.investor,
            investor_type='angel',
            organization_name='Angel Corp',
            investment_focus='AI'
        )

    def test_investor_profile_view(self):
        self.client.login(username='inv1', password='123')
        response = self.client.get(reverse('incubator:investor_profile_detail', args=[self.investor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Angel Corp')

    def test_investor_directory_search(self):
        self.client.login(username='inv1', password='123')
        response = self.client.get(reverse('incubator:investor_directory') + '?q=Angel')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Angel Corp')


class Batch8FundingTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username='fnd1', password='123', role='founder')
        self.startup = Startup.objects.create(name='Test Startup', founder=self.founder, industry='Tech')
        
        self.investor = User.objects.create_user(username='inv2', password='123', role='investor')
        
        self.round = FundingRound.objects.create(
            startup=self.startup,
            round_name='Seed Round',
            round_type='seed',
            target_amount=Decimal('100000.00'),
            minimum_amount=Decimal('10000.00'),
            opening_date=timezone.now().date(),
            closing_date=(timezone.now() + timedelta(days=30)).date(),
            status='open'
        )

    def test_funding_round_access(self):
        self.client.login(username='fnd1', password='123')
        response = self.client.get(reverse('incubator:funding_round_detail', args=[self.round.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seed Round')

    def test_funding_application_submission(self):
        self.client.login(username='inv2', password='123')
        response = self.client.post(reverse('incubator:funding_application_create', args=[self.round.id]), {
            'requested_amount': '50000.00',
            'message': 'Investing'
        })
        self.assertRedirects(response, reverse('incubator:funding_round_detail', args=[self.round.id]))
        self.assertTrue(FundingApplication.objects.filter(investor=self.investor, funding_round=self.round).exists())

    def test_investor_meeting_scheduling(self):
        app = FundingApplication.objects.create(
            funding_round=self.round, investor=self.investor, requested_amount=Decimal('50000.00')
        )
        self.client.login(username='fnd1', password='123')
        response = self.client.post(reverse('incubator:investor_meeting_create', args=[app.id]), {
            'scheduled_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'meeting_type': 'online'
        })
        self.assertRedirects(response, reverse('incubator:funding_application_detail', args=[app.id]))
        self.assertTrue(InvestorMeeting.objects.filter(funding_application=app).exists())


class Batch8HiringTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username='fnd2', password='123', role='founder')
        self.startup = Startup.objects.create(name='Hire Startup', founder=self.founder, industry='Tech')
        
        self.applicant = User.objects.create_user(username='app1', password='123', role='applicant')
        
        self.job = JobPosting.objects.create(
            startup=self.startup,
            title='Engineer',
            description='Code',
            responsibilities='Write code',
            requirements='Python',
            status='published',
            created_by=self.founder
        )

    def test_job_posting_creation_and_directory(self):
        self.client.login(username='app1', password='123')
        response = self.client.get(reverse('incubator:job_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineer')

    def test_job_application_submission(self):
        self.client.login(username='app1', password='123')
        # Simulate file upload for resume
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        
        response = self.client.post(reverse('incubator:job_application_create', args=[self.job.id]), {
            'resume': resume,
            'cover_letter': 'Hello'
        })
        self.assertRedirects(response, reverse('incubator:job_application_list'))
        self.assertTrue(JobApplication.objects.filter(applicant=self.applicant, job=self.job).exists())

    def test_interview_scheduling(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile("resume2.pdf", b"file_content", content_type="application/pdf")
        app = JobApplication.objects.create(
            job=self.job, applicant=self.applicant, resume=resume
        )
        self.client.login(username='fnd2', password='123')
        response = self.client.post(reverse('incubator:interview_create', args=[app.id]), {
            'scheduled_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'meeting_type': 'online'
        })
        self.assertRedirects(response, reverse('incubator:job_application_detail', args=[app.id]))
        self.assertTrue(Interview.objects.filter(application=app).exists())
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(new_tests)
