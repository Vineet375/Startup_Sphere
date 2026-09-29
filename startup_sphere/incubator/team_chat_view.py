
@login_required
def team_chat(request, startup_id=None):
    if startup_id:
        startup = get_object_or_404(Startup, id=startup_id)
    else:
        startup = get_active_startup(request.user)
        if not startup:
            messages.info(request, "You must register a startup first.")
            return redirect('incubator:register_startup')

    if not (request.user == startup.founder or request.user.role == 'admin' or is_active_team_member(request.user, startup) or request.user == startup.mentor):
        raise PermissionDenied

    from .models import TeamMessage
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            TeamMessage.objects.create(startup=startup, sender=request.user, content=content)
            return redirect('incubator:team_chat', startup_id=startup.id)

    messages_qs = TeamMessage.objects.filter(startup=startup)
    return render(request, 'incubator/team_chat.html', {'startup': startup, 'messages_qs': messages_qs})
