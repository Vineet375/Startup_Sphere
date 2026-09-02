
@login_required
def startup_update_status(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    if request.user != startup.mentor and request.user.role != 'admin':
        raise PermissionDenied("Only the assigned mentor or an admin can update the incubation status.")
        
    if request.method == 'POST':
        new_status = request.POST.get('incubation_status')
        if new_status in dict(Startup.INCUBATION_CHOICES):
            startup.incubation_status = new_status
            startup.save()
            messages.success(request, "Startup incubation status updated.")
            
    return redirect('incubator:startup_detail_id', startup_id=startup.id)
