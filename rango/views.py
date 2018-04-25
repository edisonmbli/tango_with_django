from datetime import datetime
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from rango.webhose_search import run_query
from registration.backends.simple.views import RegistrationView

# Index


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    visitor_cookie_handler(request)
    visits = request.session['visits']

    context_dict = {'pages': page_list,
                    'categories': category_list, 'visits': visits}

    return render(request, 'rango/index.html', context=context_dict)


# About
def about(request):
    return render(request, 'rango/about.html', {})


# Show Category
def show_category(request, category_name_slug):
    context_dict = {}

    # Prepare category and page
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    # Prepare result list
    context_dict['queryString'] = category.name
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['queryString'] = query
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


# Add Category
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


# Add Page
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
            else:
                print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


# Register
# def register(request):
#    registered = False
#
#    if request.method == 'POST':
#        user_form = UserForm(data=request.POST)
#        profile_form = UserProfileForm(data=request.POST)
#
#        if user_form.is_valid() and profile_form.is_valid():
#            user = user_form.save()
#            user.set_password(user.password)
#            user.save()
#
#            profile = profile_form.save(commit=False)
#            profile.user = user
#
#            if 'picture' in request.FILES:
#                profile.picture = request.FILES['picture']
#
#            profile.save()
#            registered = True
#        else:
#            print(user_form.errors, profile_form.errors)
#    else:
#        user_form = UserForm()
#        profile_form = UserProfileForm()
#
#    return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


# Class-based view for registration
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('register_profile')


# Register profile
@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            print(form.errors)

    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})


# Logout
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# Test Restrict
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# cookie helper function - visitor counter


# Visitor cookie
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(
        request, 'last_visit', str(datetime.now()))

    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


# Search
def search(request):
    result_list = []
    query = None

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'queryString': query, 'result_list': result_list})


# Track URL before redirect to external page
def track_url(request, page_id):

    try:
        page = Page.objects.get(id=page_id)
        page.views += 1
        page.save()
        return HttpResponseRedirect(page.url)
    except:
        print("Page id {0} not found".format(page_id))
        return HttpResponseRedirect(reverse('index'))


# Profile
@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse('profile', args=[user.username]))
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})
