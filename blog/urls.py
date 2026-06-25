from django.urls import path
from .views import home, blog_detail, trending_blogs, categories, category_blogs, like_blog
from .views import register_user, verify_otp
from .views import submit_blog
urlpatterns = [
    path('register/', register_user, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('', home, name='home'),
    path('trending/', trending_blogs, name='trending_blogs'),
    path('categories/', categories, name='categories'),
    path('category/<slug:slug>/', category_blogs, name='category_blogs'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/like/', like_blog, name='like_blog'),
    path('submit-blog/', submit_blog, name='submit_blog'),
]