import os

file_path = r'e:\Projects\GLS SEM-7 Django Project\Startup_Sphere\startup_sphere\dashboard\views.py'

code = '''
from django.db.models import Q

@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()
    
    startups = []
    users = []
    events = []
    jobs = []
    
    if query:
        startups = Startup.objects.filter(
            Q(name__icontains=query) | Q(tagline__icontains=query) | Q(category__icontains=query),
            incubation_status__in=["active", "graduated"]
        ).distinct()
        
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id).distinct()
        
        now = timezone.now()
        events = Event.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            start_datetime__gte=now,
            status="upcoming"
        ).distinct()
        
        jobs = JobPosting.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status="published"
        ).distinct()

    return render(request, "dashboard/search_results.html", {
        "query": query,
        "startups": startups,
        "users": users,
        "events": events,
        "jobs": jobs,
    })
'''

with open(file_path, 'a') as f:
    f.write('\n' + code)
