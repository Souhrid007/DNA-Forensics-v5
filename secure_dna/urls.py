"""
URL configuration for secure_dna project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    user = request.user

    # Check groups (roles)
    is_admin = user.is_superuser or user.is_staff
    is_technician = user.groups.filter(name="Technician").exists()
    is_analyst = user.groups.filter(name="Analyst").exists()

    context = {
        "is_admin": is_admin,
        "is_technician": is_technician,
        "is_analyst": is_analyst,
    }

    return render(request, "dashboard/home.html", context)



def logout_view(request):
    """
    Simple logout: clear session and send user to login page.
    """
    logout(request)
    return redirect('login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # Auth
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='accounts/login.html'),
         name='login'),
    path('accounts/logout/', logout_view, name='logout'),

    # Our apps
    path('', include('cases.urls')),
    path('', include('strprofiles.urls')),
    path('', include('matching.urls')),
    path('', include('reporting.urls')),
    path('', include('auditlog.urls')),

]



