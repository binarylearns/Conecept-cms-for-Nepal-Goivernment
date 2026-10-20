
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import AuthorCreateForm
from authorapp.models import AuthorProfile
# from django.views.decorators.http import require_POST



def is_coadmin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Co-admin").exists()
        )
    )


@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated:
        if is_coadmin(request.user):
            return redirect("coadmin:home")
        return redirect("coadmin:login")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if is_coadmin(user):
                auth_login(request, user)
                return redirect("coadmin:home")

            messages.error(
                request,
                "You do not have permission to access the co-admin dashboard."
            )
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "dashboard/login.html")


@login_required
def home(request):
    if not is_coadmin(request.user):
        raise PermissionDenied

    stats = {
        "authors": AuthorProfile.objects.count(),
        "articles": 48,
        "pending": 7,
        "published": 35,
    }

    return render(request, "dashboard/home.html", {"stats": stats})


@login_required
@require_http_methods(["GET", "POST"])
def create_author(request):
    if not is_coadmin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = AuthorCreateForm(request.POST)

        if form.is_valid():
            user = form.save()

            author_group, _ = Group.objects.get_or_create(
                name="Author"
            )
            user.groups.add(author_group)

            messages.success(
                request,
                f"Author '{user.username}' created successfully."
            )
            return redirect("coadmin:author_list")
    else:
        form = AuthorCreateForm()

    return render(
        request,
        "coadmin/create_author.html",
        {"form": form},
    )


@login_required
def author_list(request):
    if not is_coadmin(request.user):
        raise PermissionDenied

    authors = AuthorProfile.objects.select_related(
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "coadmin/author_list.html",
        {"authors": authors},
    )


# @login_required
# @require_POST
# def logout_view(request):
#     logout(request)
#     return redirect("coadmin:login")