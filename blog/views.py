import random
from django.contrib import messages
from .models import Blog, Category, Comment, Rating, BlogLike
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm, OTPForm
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Blog, Category, Comment, Rating
from django.contrib.auth.decorators import login_required
from .forms import BlogSubmitForm
def home(request):

    query = request.GET.get('q')

    blogs = Blog.objects.filter(status='published').annotate(
        average_rating=Avg('ratings__rating')
    )

    if query:
        blogs = blogs.filter(title__icontains=query)

    return render(request, 'home.html', {
        'blogs': blogs,
        'query': query
    })


def trending_blogs(request):
    blogs = Blog.objects.filter(status='published').annotate(
        average_rating=Avg('ratings__rating')
    ).order_by('-created_at')

    return render(request, 'home.html', {
        'blogs': blogs,
        'page_title': 'Trending Blogs'
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {
        'categories': categories
    })


def category_blogs(request, slug):
    category = get_object_or_404(Category, slug=slug)

    blogs = Blog.objects.filter(
        category=category,
        status='published'
    ).annotate(
        average_rating=Avg('ratings__rating')
    )

    return render(request, 'home.html', {
        'blogs': blogs,
        'page_title': category.name
    })


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')

    blog.views += 1
    blog.save()

    if request.method == "POST":
        if "comment_submit" in request.POST:
            name = request.POST.get("name")
            comment_text = request.POST.get("comment")

            Comment.objects.create(
                blog=blog,
                name=name,
                comment=comment_text
            )

            return redirect('blog_detail', slug=blog.slug)

        if "rating_submit" in request.POST:
            name = request.POST.get("rating_name")
            rating_value = request.POST.get("rating")
            review = request.POST.get("review")

            Rating.objects.create(
                blog=blog,
                name=name,
                rating=rating_value,
                review=review
            )

            return redirect('blog_detail', slug=blog.slug)

    comments = blog.comments.filter(is_approved=True)
    ratings = blog.ratings.all()
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'ratings': ratings,
        'average_rating': average_rating,
    })

@login_required
def like_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    like, created = BlogLike.objects.get_or_create(
        blog=blog,
        user=request.user
    )

    if created:
        blog.likes += 1
        blog.save()
        messages.success(request, "You liked this blog.")
    else:
        messages.info(request, "You have already liked this blog.")

    return redirect('blog_detail', slug=blog.slug)
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('register')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('register')

            otp = random.randint(100000, 999999)

            request.session['register_username'] = username
            request.session['register_email'] = email
            request.session['register_password'] = password
            request.session['register_otp'] = str(otp)

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email.")
            return redirect('verify_otp')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def verify_otp(request):
    if request.method == "POST":
        form = OTPForm(request.POST)

        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            saved_otp = request.session.get('register_otp')

            if entered_otp == saved_otp:
                username = request.session.get('register_username')
                email = request.session.get('register_email')
                password = request.session.get('register_password')

                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                request.session.flush()

                messages.success(request, "Account created successfully. You can login now.")
                return redirect('login')

            else:
                messages.error(request, "Invalid OTP.")

    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})
@login_required
def submit_blog(request):
    if request.method == "POST":
        form = BlogSubmitForm(request.POST, request.FILES)

        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.status = 'draft'
            blog.save()
            form.save_m2m()

            return render(request, 'blog_submitted.html')

    else:
        form = BlogSubmitForm()

    return render(request, 'submit_blog.html', {
        'form': form
    })