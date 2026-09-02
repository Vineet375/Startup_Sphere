
from django.views.decorators.http import require_POST

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'incubator/notification_list.html', {'notifications': notifications})

@login_required
@require_POST
def notification_mark_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # After marking as read, optionally redirect to the link URL if provided in the form POST (as a next parameter)
    # But for a simple AJAX or form submit, we might just redirect back to notifications page
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('incubator:notification_list')

@login_required
@require_POST
def notification_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('incubator:notification_list')
