import re

content = open('incubator/views.py', 'r', encoding='utf-8').read()

# startup_registered
if 'activity_type=\'startup_registered\'' not in content:
    content = content.replace(
        'startup.save()\n            messages.success(request, "Your startup has been registered successfully!")',
        '''startup.save()
            Activity.objects.create(
                startup=startup,
                user=request.user,
                activity_type='startup_registered',
                description=f'Startup "{startup.name}" was registered.'
            )
            messages.success(request, "Your startup has been registered successfully!")'''
    )

# idea_edit
content = content.replace(
'''            if 'submit' in request.POST:
                idea.status = 'submitted'
                idea.submitted_at = timezone.now()
                messages.success(request, "Your idea has been submitted successfully!")''',
'''            if 'submit' in request.POST:
                idea.status = 'submitted'
                idea.submitted_at = timezone.now()
                Activity.objects.create(
                    startup=idea.startup,
                    user=request.user,
                    activity_type='idea_submitted',
                    description=f'Idea "{idea.title}" was submitted.'
                )
                if idea.startup.mentor:
                    Notification.objects.create(
                        recipient=idea.startup.mentor,
                        actor=request.user,
                        startup=idea.startup,
                        title="Idea Submitted",
                        message=f"{idea.startup.name} has submitted a new idea: {idea.title}.",
                        notification_type='idea_submitted',
                        link_url=reverse('incubator:idea_detail', args=[idea.id])
                    )
                messages.success(request, "Your idea has been submitted successfully!")'''
)

# idea_submit
content = content.replace(
'''        idea.status = 'submitted'
        idea.submitted_at = timezone.now()
        idea.save()
        messages.success(request, "Your idea has been submitted successfully!")''',
'''        idea.status = 'submitted'
        idea.submitted_at = timezone.now()
        idea.save()
        Activity.objects.create(
            startup=idea.startup,
            user=request.user,
            activity_type='idea_submitted',
            description=f'Idea "{idea.title}" was submitted.'
        )
        if idea.startup.mentor:
            Notification.objects.create(
                recipient=idea.startup.mentor,
                actor=request.user,
                startup=idea.startup,
                title="Idea Submitted",
                message=f"{idea.startup.name} has submitted a new idea: {idea.title}.",
                notification_type='idea_submitted',
                link_url=reverse('incubator:idea_detail', args=[idea.id])
            )
        messages.success(request, "Your idea has been submitted successfully!")'''
)

# add_feedback
content = content.replace(
'''            feedback.mentor = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully.")''',
'''            feedback.mentor = request.user
            feedback.save()
            Activity.objects.create(
                startup=idea.startup,
                user=request.user,
                activity_type='feedback_added',
                description=f'Mentor provided feedback on "{idea.title}".'
            )
            Notification.objects.create(
                recipient=idea.startup.founder,
                actor=request.user,
                startup=idea.startup,
                title="New Feedback Received",
                message=f"Mentor {request.user.get_full_name() or request.user.username} provided feedback on your idea: {idea.title}.",
                notification_type='feedback_received',
                link_url=reverse('incubator:idea_detail', args=[idea.id])
            )
            messages.success(request, "Feedback submitted successfully.")'''
)

# mark_under_review
content = content.replace(
'''        idea.status = 'under_review'
        idea.save()
        messages.success(request, "Idea status changed to Under Review.")''',
'''        idea.status = 'under_review'
        idea.save()
        Activity.objects.create(
            startup=idea.startup,
            user=request.user,
            activity_type='idea_under_review',
            description=f'Mentor marked the idea "{idea.title}" as Under Review.'
        )
        Notification.objects.create(
            recipient=idea.startup.founder,
            actor=request.user,
            startup=idea.startup,
            title="Idea Under Review",
            message=f'Your idea "{idea.title}" is now under review.',
            notification_type='idea_under_review',
            link_url=reverse('incubator:idea_detail', args=[idea.id])
        )
        messages.success(request, "Idea status changed to Under Review.")'''
)

# milestone_create
content = content.replace(
'''            milestone.startup = startup
            milestone.save()
            messages.success(request, "Milestone created successfully.")''',
'''            milestone.startup = startup
            milestone.save()
            Activity.objects.create(
                startup=startup,
                user=request.user,
                activity_type='milestone_created',
                description=f'Milestone "{milestone.title}" was created.'
            )
            Notification.objects.create(
                recipient=startup.founder,
                actor=request.user,
                startup=startup,
                title="New Milestone Created",
                message=f'A new milestone "{milestone.title}" has been created for your startup.',
                notification_type='milestone_created',
                link_url=reverse('incubator:startup_detail')
            )
            messages.success(request, "Milestone created successfully.")'''
)

# milestone_update
content = content.replace(
'''        if is_mentor_or_admin:
            form = MilestoneForm(request.POST, instance=milestone)
        else:
            # Founder can only update status
            form = MilestoneForm(instance=milestone)
            new_status = request.POST.get('status')
            if new_status in dict(Milestone.STATUS_CHOICES):
                milestone.status = new_status
                milestone.save()
                messages.success(request, "Milestone status updated.")
                return redirect('incubator:startup_detail')
                
        if form.is_valid() and is_mentor_or_admin:
            form.save()
            messages.success(request, "Milestone updated successfully.")''',
'''        old_status = milestone.status
        if is_mentor_or_admin:
            form = MilestoneForm(request.POST, instance=milestone)
        else:
            # Founder can only update status
            form = MilestoneForm(instance=milestone)
            new_status = request.POST.get('status')
            if new_status in dict(Milestone.STATUS_CHOICES):
                milestone.status = new_status
                milestone.save()
                if old_status != 'completed' and new_status == 'completed':
                    Activity.objects.create(
                        startup=startup, user=request.user, activity_type='milestone_completed',
                        description=f'Milestone "{milestone.title}" was completed.'
                    )
                    if startup.mentor:
                        Notification.objects.create(
                            recipient=startup.mentor,
                            actor=request.user,
                            startup=startup,
                            title="Milestone Completed",
                            message=f'Milestone "{milestone.title}" for {startup.name} was marked as completed.',
                            notification_type='milestone_completed',
                            link_url=reverse('incubator:startup_detail', args=[startup.id])
                        )
                elif old_status != new_status:
                    Activity.objects.create(
                        startup=startup, user=request.user, activity_type='milestone_updated',
                        description=f'Milestone "{milestone.title}" status changed to {dict(Milestone.STATUS_CHOICES).get(new_status, new_status)}.'
                    )
                messages.success(request, "Milestone status updated.")
                return redirect('incubator:startup_detail')
                
        if form.is_valid() and is_mentor_or_admin:
            milestone = form.save()
            if old_status != 'completed' and milestone.status == 'completed':
                Activity.objects.create(
                    startup=startup, user=request.user, activity_type='milestone_completed',
                    description=f'Milestone "{milestone.title}" was completed.'
                )
            else:
                Activity.objects.create(
                    startup=startup, user=request.user, activity_type='milestone_updated',
                    description=f'Milestone "{milestone.title}" was updated.'
                )
            messages.success(request, "Milestone updated successfully.")'''
)

open('incubator/views.py', 'w', encoding='utf-8').write(content)
