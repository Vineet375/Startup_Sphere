from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    role = request.user.role
    # For now, just render a generic dashboard, we will redirect later based on role
    return render(request, 'dashboard/home.html', {'role': role})
