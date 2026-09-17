import os

file_path = 'batch8_views.py'
content = """
from .models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from .forms import InvestorProfileForm, FundingRoundForm, FundingApplicationForm, InvestorMeetingForm, JobPostingForm, JobApplicationForm, InterviewForm
from django.db.models import Sum

# ----------------- INVESTOR PROFILES -----------------

@login_required
def investor_profile_edit(request):
    if request.user.role != 'investor':
        raise PermissionDenied

    profile, created = InvestorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Investor profile updated successfully.')
            return redirect('incubator:investor_profile_detail', user_id=request.user.id)
    else:
        form = InvestorProfileForm(instance=profile)
    return render(request, 'incubator/investor_profile_form.html', {'form': form})

@login_required
def investor_profile_detail(request, user_id):
    investor_user = get_object_or_404(User, id=user_id, role='investor')
    profile = get_object_or_404(InvestorProfile, user=investor_user)
    return render(request, 'incubator/investor_profile_detail.html', {'profile': profile})

@login_required
def investor_directory(request):
    query = request.GET.get('q', '')
    investor_type = request.GET.get('investor_type', '')
    
    profiles = InvestorProfile.objects.select_related('user').all().order_by('-created_at')
    
    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(organization_name__icontains=query) |
            Q(investment_focus__icontains=query)
        )
    if investor_type:
        profiles = profiles.filter(investor_type=investor_type)
        
    return render(request, 'incubator/investor_directory.html', {'profiles': profiles, 'query': query, 'investor_type': investor_type})


# ----------------- FUNDING ROUNDS -----------------

@login_required
def funding_round_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        if not startup:
            messages.warning(request, "Register a startup first.")
            return redirect('dashboard:home')
        rounds = FundingRound.objects.filter(startup=startup).order_by('-created_at')
        is_founder = True
    else:
        # Investor view: open rounds
        rounds = FundingRound.objects.filter(status='open').order_by('-created_at')
        is_founder = False
        
    return render(request, 'incubator/funding_round_list.html', {'rounds': rounds, 'is_founder': is_founder})

@login_required
def funding_round_detail(request, round_id):
    funding_round = get_object_or_404(FundingRound, id=round_id)
    startup = funding_round.startup
    
    is_owner = (request.user.role == 'founder' and startup.founder == request.user)
    has_access = is_owner or request.user.role in ['admin', 'investor']
    
    if request.user.role == 'mentor':
        has_access = startup in request.user.mentored_startups.all()
    if request.user.role == 'team_member':
        has_access = startup == get_active_startup(request.user)
        
    if not has_access:
        raise PermissionDenied
        
    applications = []
    has_applied = False
    my_application = None
    
    if is_owner or request.user.role == 'admin':
        applications = funding_round.applications.all().order_by('-created_at')
    elif request.user.role == 'investor':
        my_application = funding_round.applications.filter(investor=request.user).first()
        if my_application:
            has_applied = True
            
    return render(request, 'incubator/funding_round_detail.html', {
        'round': funding_round,
        'applications': applications,
        'is_owner': is_owner,
        'has_applied': has_applied,
        'my_application': my_application
    })

@login_required
def funding_round_create(request):
    if request.user.role != 'founder':
        raise PermissionDenied
    startup = get_active_startup(request.user)
    if not startup or startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = FundingRoundForm(request.POST)
        if form.is_valid():
            rnd = form.save(commit=False)
            rnd.startup = startup
            rnd.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='funding_round_created', description=f"Funding round {rnd.round_name} created.")
            messages.success(request, 'Funding round created.')
            return redirect('incubator:funding_round_list')
    else:
        form = FundingRoundForm()
    return render(request, 'incubator/funding_round_form.html', {'form': form, 'title': 'Create Funding Round'})

@login_required
def funding_round_edit(request, round_id):
    funding_round = get_object_or_404(FundingRound, id=round_id)
    if request.user.role != 'founder' or funding_round.startup.founder != request.user:
        raise PermissionDenied
        
    old_status = funding_round.status
    if request.method == 'POST':
        form = FundingRoundForm(request.POST, instance=funding_round)
        if form.is_valid():
            rnd = form.save()
            if old_status != rnd.status:
                if rnd.status == 'open':
                    Activity.objects.create(startup=rnd.startup, user=request.user, activity_type='funding_round_opened', description=f"Funding round {rnd.round_name} opened.")
                elif rnd.status == 'closed':
                    Activity.objects.create(startup=rnd.startup, user=request.user, activity_type='funding_round_closed', description=f"Funding round {rnd.round_name} closed.")
            messages.success(request, 'Funding round updated.')
            return redirect('incubator:funding_round_detail', round_id=rnd.id)
    else:
        form = FundingRoundForm(instance=funding_round)
    return render(request, 'incubator/funding_round_form.html', {'form': form, 'title': 'Edit Funding Round'})

# ----------------- FUNDING APPLICATIONS -----------------

@login_required
def funding_application_create(request, round_id):
    if request.user.role != 'investor':
        raise PermissionDenied
        
    funding_round = get_object_or_404(FundingRound, id=round_id)
    if funding_round.status != 'open':
        messages.error(request, "This funding round is not open for applications.")
        return redirect('incubator:funding_round_detail', round_id=funding_round.id)
        
    if FundingApplication.objects.filter(funding_round=funding_round, investor=request.user).exists():
        messages.warning(request, "You have already applied to this round.")
        return redirect('incubator:funding_round_detail', round_id=funding_round.id)

    if request.method == 'POST':
        form = FundingApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.funding_round = funding_round
            app.investor = request.user
            app.save()
            
            Activity.objects.create(startup=funding_round.startup, user=request.user, activity_type='funding_application_submitted', description=f"Funding application submitted by {request.user.username}.")
            Notification.objects.create(
                recipient=funding_round.startup.founder,
                actor=request.user,
                startup=funding_round.startup,
                title="New Funding Application",
                message=f"{request.user.username} submitted a funding application for {funding_round.round_name}.",
                notification_type='funding_application_received',
                link_url=reverse('incubator:funding_application_detail', args=[app.id])
            )
            messages.success(request, 'Application submitted successfully.')
            return redirect('incubator:funding_round_detail', round_id=funding_round.id)
    else:
        form = FundingApplicationForm()
    return render(request, 'incubator/funding_application_form.html', {'form': form, 'round': funding_round})


@login_required
def funding_application_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        applications = FundingApplication.objects.filter(funding_round__startup=startup).order_by('-created_at')
    elif request.user.role == 'investor':
        applications = FundingApplication.objects.filter(investor=request.user).order_by('-created_at')
    else:
        raise PermissionDenied
        
    return render(request, 'incubator/funding_application_list.html', {'applications': applications})

@login_required
def funding_application_detail(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    is_owner = (request.user.role == 'founder' and app.funding_round.startup.founder == request.user)
    is_investor = (request.user == app.investor)
    
    if not (is_owner or is_investor or request.user.role == 'admin'):
        raise PermissionDenied
        
    meetings = app.meetings.all().order_by('-scheduled_at')
    
    if request.method == 'POST' and is_owner:
        new_status = request.POST.get('status')
        if new_status in dict(FundingApplication.STATUS_CHOICES).keys():
            app.status = new_status
            app.responded_at = timezone.now()
            app.save()
            
            # Record activity and notify
            Activity.objects.create(startup=app.funding_round.startup, user=request.user, activity_type='funding_application_status_changed', description=f"Application status changed to {new_status}.")
            
            notif_type_map = {
                'reviewing': 'funding_application_reviewing',
                'accepted': 'funding_application_accepted',
                'rejected': 'funding_application_rejected',
            }
            Notification.objects.create(
                recipient=app.investor,
                actor=request.user,
                startup=app.funding_round.startup,
                title=f"Funding Application {new_status.title()}",
                message=f"Your application for {app.funding_round.round_name} is now {new_status}.",
                notification_type=notif_type_map.get(new_status, 'funding_application_received'),
                link_url=reverse('incubator:funding_application_detail', args=[app.id])
            )
            messages.success(request, f"Status updated to {new_status}.")
            return redirect('incubator:funding_application_detail', app_id=app.id)
            
    return render(request, 'incubator/funding_application_detail.html', {'app': app, 'meetings': meetings, 'is_owner': is_owner, 'is_investor': is_investor})

@login_required
def funding_application_withdraw(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    if request.user != app.investor:
        raise PermissionDenied
    if request.method == 'POST':
        app.status = 'withdrawn'
        app.save()
        messages.success(request, "Application withdrawn.")
    return redirect('incubator:funding_application_detail', app_id=app.id)


# ----------------- INVESTOR MEETINGS -----------------

@login_required
def investor_meeting_create(request, app_id):
    app = get_object_or_404(FundingApplication, id=app_id)
    if request.user.role != 'founder' or app.funding_round.startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = InvestorMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.funding_application = app
            meeting.organizer = request.user
            meeting.save()
            
            Activity.objects.create(startup=app.funding_round.startup, user=request.user, activity_type='investor_meeting_scheduled', description=f"Meeting scheduled with {app.investor.username}.")
            Notification.objects.create(
                recipient=app.investor,
                actor=request.user,
                startup=app.funding_round.startup,
                title="Funding Meeting Scheduled",
                message=f"A meeting has been scheduled regarding your application for {app.funding_round.startup.name}.",
                notification_type='funding_meeting_scheduled',
                link_url=reverse('incubator:investor_meeting_detail', args=[meeting.id])
            )
            messages.success(request, 'Meeting scheduled successfully.')
            return redirect('incubator:funding_application_detail', app_id=app.id)
    else:
        form = InvestorMeetingForm()
    return render(request, 'incubator/investor_meeting_form.html', {'form': form, 'app': app})

@login_required
def investor_meeting_detail(request, meeting_id):
    meeting = get_object_or_404(InvestorMeeting, id=meeting_id)
    is_owner = (request.user.role == 'founder' and meeting.funding_application.funding_round.startup.founder == request.user)
    is_investor = (request.user == meeting.funding_application.investor)
    
    if not (is_owner or is_investor or request.user.role == 'admin'):
        raise PermissionDenied
        
    if request.method == 'POST' and is_owner:
        action = request.POST.get('action')
        if action in ['completed', 'cancelled']:
            meeting.status = action
            meeting.save()
            if action == 'cancelled':
                Notification.objects.create(
                    recipient=meeting.funding_application.investor,
                    actor=request.user,
                    startup=meeting.funding_application.funding_round.startup,
                    title="Meeting Cancelled",
                    message=f"Your meeting for {meeting.funding_application.funding_round.startup.name} was cancelled.",
                    notification_type='funding_meeting_cancelled',
                    link_url=reverse('incubator:investor_meeting_detail', args=[meeting.id])
                )
            messages.success(request, f"Meeting marked as {action}.")
        return redirect('incubator:investor_meeting_detail', meeting_id=meeting.id)

    return render(request, 'incubator/investor_meeting_detail.html', {'meeting': meeting, 'is_owner': is_owner, 'is_investor': is_investor})


# ----------------- HIRING & JOB POSTINGS -----------------

@login_required
def job_posting_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        jobs = JobPosting.objects.filter(startup=startup).order_by('-created_at')
        is_founder = True
    else:
        # Public directory
        return redirect('incubator:job_directory')
        
    return render(request, 'incubator/job_posting_list.html', {'jobs': jobs, 'is_founder': is_founder})

@login_required
def job_directory(request):
    query = request.GET.get('q', '')
    emp_type = request.GET.get('employment_type', '')
    exp_level = request.GET.get('experience_level', '')
    
    jobs = JobPosting.objects.filter(status='published').order_by('-created_at')
    
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(startup__name__icontains=query))
    if emp_type:
        jobs = jobs.filter(employment_type=emp_type)
    if exp_level:
        jobs = jobs.filter(experience_level=exp_level)
        
    return render(request, 'incubator/job_directory.html', {'jobs': jobs, 'query': query, 'emp_type': emp_type, 'exp_level': exp_level})

@login_required
def job_posting_detail(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    startup = job.startup
    
    is_owner = (request.user.role == 'founder' and startup.founder == request.user)
    has_access = is_owner or request.user.role in ['admin', 'applicant']
    
    if request.user.role == 'mentor':
        has_access = startup in request.user.mentored_startups.all()
    if request.user.role == 'team_member':
        has_access = startup == get_active_startup(request.user)
    if request.user.role == 'investor' and job.status == 'published':
        has_access = True
        
    if not has_access and job.status != 'published':
        raise PermissionDenied
        
    applications = []
    my_application = None
    if is_owner or request.user.role == 'admin':
        applications = job.applications.all().order_by('-applied_at')
    elif request.user.role == 'applicant':
        my_application = job.applications.filter(applicant=request.user).first()
        
    return render(request, 'incubator/job_posting_detail.html', {
        'job': job, 'applications': applications, 'is_owner': is_owner, 'my_application': my_application
    })

@login_required
def job_posting_create(request):
    if request.user.role != 'founder':
        raise PermissionDenied
    startup = get_active_startup(request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.startup = startup
            job.created_by = request.user
            job.save()
            Activity.objects.create(startup=startup, user=request.user, activity_type='job_posting_created', description=f"Job posting {job.title} created.")
            messages.success(request, 'Job posting created.')
            return redirect('incubator:job_posting_list')
    else:
        form = JobPostingForm()
    return render(request, 'incubator/job_posting_form.html', {'form': form, 'title': 'Create Job Posting'})

@login_required
def job_posting_edit(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.user.role != 'founder' or job.startup.founder != request.user:
        raise PermissionDenied
        
    old_status = job.status
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            j = form.save()
            if old_status != j.status:
                if j.status == 'published':
                    Activity.objects.create(startup=j.startup, user=request.user, activity_type='job_published', description=f"Job {j.title} published.")
                elif j.status == 'closed':
                    Activity.objects.create(startup=j.startup, user=request.user, activity_type='job_closed', description=f"Job {j.title} closed.")
            messages.success(request, 'Job posting updated.')
            return redirect('incubator:job_posting_detail', job_id=j.id)
    else:
        form = JobPostingForm(instance=job)
    return render(request, 'incubator/job_posting_form.html', {'form': form, 'title': 'Edit Job Posting'})


# ----------------- JOB APPLICATIONS -----------------

@login_required
def job_application_create(request, job_id):
    if request.user.role != 'applicant':
        messages.error(request, "Only applicants can apply for jobs.")
        return redirect('incubator:job_posting_detail', job_id=job_id)
        
    job = get_object_or_404(JobPosting, id=job_id)
    if job.status != 'published':
        messages.error(request, "This job is not accepting applications.")
        return redirect('incubator:job_posting_detail', job_id=job.id)
        
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('incubator:job_posting_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            app.save()
            
            Activity.objects.create(startup=job.startup, user=request.user, activity_type='job_application_submitted', description=f"Job application submitted by {request.user.username}.")
            Notification.objects.create(
                recipient=job.startup.founder,
                actor=request.user,
                startup=job.startup,
                title="New Job Application",
                message=f"{request.user.username} applied for {job.title}.",
                notification_type='job_application_received',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, 'Application submitted successfully.')
            return redirect('incubator:job_application_list')
    else:
        form = JobApplicationForm()
    return render(request, 'incubator/job_application_form.html', {'form': form, 'job': job})


@login_required
def job_application_list(request):
    if request.user.role == 'founder':
        startup = get_active_startup(request.user)
        applications = JobApplication.objects.filter(job__startup=startup).order_by('-applied_at')
    elif request.user.role == 'applicant':
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    else:
        raise PermissionDenied
        
    return render(request, 'incubator/job_application_list.html', {'applications': applications})

@login_required
def job_application_detail(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    is_owner = (request.user.role == 'founder' and app.job.startup.founder == request.user)
    is_applicant = (request.user == app.applicant)
    
    if not (is_owner or is_applicant or request.user.role == 'admin'):
        raise PermissionDenied
        
    interviews = app.interviews.all().order_by('-scheduled_at')
    
    if request.method == 'POST' and is_owner:
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES).keys():
            app.status = new_status
            app.save()
            
            if new_status == 'shortlisted':
                Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='job_application_shortlisted', description=f"Application shortlisted.")
            elif new_status == 'rejected':
                Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='job_application_rejected', description=f"Application rejected.")

            Notification.objects.create(
                recipient=app.applicant,
                actor=request.user,
                startup=app.job.startup,
                title="Application Status Updated",
                message=f"Your application for {app.job.title} is now {new_status}.",
                notification_type='job_application_status_changed',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, f"Status updated to {new_status}.")
            return redirect('incubator:job_application_detail', app_id=app.id)
            
    return render(request, 'incubator/job_application_detail.html', {'app': app, 'interviews': interviews, 'is_owner': is_owner, 'is_applicant': is_applicant})


# ----------------- INTERVIEWS -----------------

@login_required
def interview_create(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    if request.user.role != 'founder' or app.job.startup.founder != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = app
            interview.interviewer = request.user
            interview.save()
            
            Activity.objects.create(startup=app.job.startup, user=request.user, activity_type='interview_scheduled', description=f"Interview scheduled with {app.applicant.username}.")
            Notification.objects.create(
                recipient=app.applicant,
                actor=request.user,
                startup=app.job.startup,
                title="Interview Scheduled",
                message=f"An interview has been scheduled for your application to {app.job.title}.",
                notification_type='interview_scheduled',
                link_url=reverse('incubator:job_application_detail', args=[app.id])
            )
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('incubator:job_application_detail', app_id=app.id)
    else:
        form = InterviewForm()
    return render(request, 'incubator/interview_form.html', {'form': form, 'app': app})
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Now write a script to append to incubator/views.py
append_script = """import os
with open('batch8_views.py', 'r', encoding='utf-8') as f:
    new_views = f.read()

with open('incubator/views.py', 'a', encoding='utf-8') as f:
    f.write(new_views)
"""
with open('do_append_views.py', 'w', encoding='utf-8') as f:
    f.write(append_script)

