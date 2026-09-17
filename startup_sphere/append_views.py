import os

file_path = 'batch7_views.py'
content = """
from django.db.models import Q
from django.utils import timezone
from .models import Event, EventParticipation, CollaborationRequest
from .forms import EventForm, CollaborationRequestForm

# ----------------- EVENTS MODULE -----------------

@login_required
def event_list(request):
    now = timezone.now()
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'upcoming')
    
    events = Event.objects.all().order_by('start_datetime')
    
    if status_filter:
        events = events.filter(status=status_filter)
        
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    registered_event_ids = []
    if request.user.is_authenticated:
        registered_event_ids = EventParticipation.objects.filter(participant=request.user, status='registered').values_list('event_id', flat=True)
        
    return render(request, 'incubator/event_list.html', {
        'events': events,
        'registered_event_ids': registered_event_ids,
        'query': query,
        'status_filter': status_filter,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = EventParticipation.objects.filter(event=event, participant=request.user).first()
    
    # Check if full
    current_participants = event.participations.filter(status='registered').count()
    is_full = event.capacity is not None and current_participants >= event.capacity
    
    return render(request, 'incubator/event_detail.html', {
        'event': event,
        'participation': participation,
        'is_full': is_full,
        'current_participants': current_participants
    })

@login_required
def event_create(request):
    if request.user.role not in ['admin', 'mentor']:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('incubator:event_list')
    else:
        form = EventForm()
        
    return render(request, 'incubator/event_form.html', {'form': form, 'title': 'Create Event'})

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('incubator:event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
        
    return render(request, 'incubator/event_form.html', {'form': form, 'title': 'Edit Event'})

@login_required
def event_cancel(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        event.status = 'cancelled'
        event.save()
        
        # Notify participants
        for p in event.participations.filter(status='registered'):
            Notification.objects.create(
                recipient=p.participant,
                title=f"Event Cancelled: {event.title}",
                message=f"The event {event.title} has been cancelled.",
                notification_type='event_cancelled_notify'
            )
            
        messages.success(request, 'Event cancelled successfully!')
        return redirect('incubator:event_detail', event_id=event.id)
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_register(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.status != 'upcoming':
        messages.error(request, 'You can only register for upcoming events.')
        return redirect('incubator:event_detail', event_id=event.id)
        
    current_participants = event.participations.filter(status='registered').count()
    if event.capacity and current_participants >= event.capacity:
        messages.error(request, 'This event is already full.')
        return redirect('incubator:event_detail', event_id=event.id)
        
    participation, created = EventParticipation.objects.get_or_create(
        event=event,
        participant=request.user,
        defaults={'status': 'registered'}
    )
    
    if not created:
        if participation.status == 'cancelled':
            participation.status = 'registered'
            participation.save()
            messages.success(request, 'Re-registered for event.')
        else:
            messages.info(request, 'You are already registered for this event.')
    else:
        Notification.objects.create(
            recipient=request.user,
            title="Event Registration Successful",
            message=f"You have registered for {event.title}.",
            notification_type='event_registered',
            link_url=f"/incubator/events/{event.id}/"
        )
        messages.success(request, 'Successfully registered for event!')
        
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_unregister(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = get_object_or_404(EventParticipation, event=event, participant=request.user)
    
    if request.method == 'POST':
        participation.status = 'cancelled'
        participation.save()
        messages.success(request, 'Your registration has been cancelled.')
        
    return redirect('incubator:event_detail', event_id=event.id)

@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    participants = event.participations.all().order_by('-registered_at')
    return render(request, 'incubator/event_participants.html', {'event': event, 'participants': participants})

@login_required
def event_mark_attendance(request, event_id, participation_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.role != 'admin' and event.organizer != request.user:
        raise PermissionDenied
        
    participation = get_object_or_404(EventParticipation, id=participation_id, event=event)
    if request.method == 'POST':
        participation.status = 'attended'
        participation.attended_at = timezone.now()
        participation.save()
        messages.success(request, 'Attendance marked successfully.')
        
    return redirect('incubator:event_participants', event_id=event.id)


# ----------------- COLLABORATION MODULE -----------------

@login_required
def collaboration_directory(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id).order_by('username')
    
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        
    return render(request, 'incubator/collaboration_directory.html', {'users': users, 'query': query})

@login_required
def collaboration_request_create(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if recipient == request.user:
        messages.error(request, "You cannot send a collaboration request to yourself.")
        return redirect('incubator:collaboration_directory')
        
    requester_startup = get_active_startup(request.user)
    recipient_startup = get_active_startup(recipient)
    
    if requester_startup and recipient_startup and requester_startup == recipient_startup:
        messages.error(request, "You cannot send a collaboration request to someone in your own startup.")
        return redirect('incubator:collaboration_directory')
        
    # Check duplicate
    existing = CollaborationRequest.objects.filter(requester=request.user, recipient=recipient, status='pending').exists()
    if existing:
        messages.warning(request, "You already have a pending request with this user.")
        return redirect('incubator:collaboration_directory')

    if request.method == 'POST':
        form = CollaborationRequestForm(request.POST)
        if form.is_valid():
            collab = form.save(commit=False)
            collab.requester = request.user
            collab.recipient = recipient
            collab.requester_startup = requester_startup
            collab.recipient_startup = recipient_startup
            collab.save()
            
            Notification.objects.create(
                recipient=recipient,
                actor=request.user,
                title="New Collaboration Request",
                message=f"You received a collaboration request from {request.user.get_full_name() or request.user.username}.",
                notification_type='collaboration_received',
                link_url=reverse('incubator:collaboration_detail', args=[collab.id])
            )
            messages.success(request, 'Collaboration request sent successfully.')
            return redirect('incubator:collaboration_list')
    else:
        form = CollaborationRequestForm()
        
    return render(request, 'incubator/collaboration_form.html', {'form': form, 'recipient': recipient})

@login_required
def collaboration_list(request):
    sent_requests = CollaborationRequest.objects.filter(requester=request.user).order_by('-created_at')
    received_requests = CollaborationRequest.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'incubator/collaboration_list.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

@login_required
def collaboration_detail(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user not in [collab.requester, collab.recipient] and request.user.role != 'admin':
        raise PermissionDenied
        
    return render(request, 'incubator/collaboration_detail.html', {'collab': collab})

@login_required
def collaboration_accept(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.recipient:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'accepted'
        collab.responded_at = timezone.now()
        collab.save()
        
        Notification.objects.create(
            recipient=collab.requester,
            actor=request.user,
            title="Collaboration Request Accepted",
            message=f"{request.user.username} accepted your request.",
            notification_type='collaboration_accepted',
            link_url=reverse('incubator:collaboration_detail', args=[collab.id])
        )
        messages.success(request, 'Request accepted.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)

@login_required
def collaboration_reject(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.recipient:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'rejected'
        collab.responded_at = timezone.now()
        collab.save()
        
        Notification.objects.create(
            recipient=collab.requester,
            actor=request.user,
            title="Collaboration Request Rejected",
            message=f"{request.user.username} declined your request.",
            notification_type='collaboration_rejected',
            link_url=reverse('incubator:collaboration_detail', args=[collab.id])
        )
        messages.success(request, 'Request rejected.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)

@login_required
def collaboration_cancel(request, request_id):
    collab = get_object_or_404(CollaborationRequest, id=request_id)
    if request.user != collab.requester:
        raise PermissionDenied
        
    if request.method == 'POST':
        collab.status = 'cancelled'
        collab.save()
        messages.success(request, 'Request cancelled.')
    return redirect('incubator:collaboration_detail', request_id=collab.id)

"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Append to incubator/views.py
with open('incubator/views.py', 'a', encoding='utf-8') as f:
    f.write(content)

