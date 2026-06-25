from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import Category, Tag, Blog, Comment, UserProfile, Rating, BlogLike


admin.site.site_header = "Blog Management System's Admin"
admin.site.site_title = "BMS Admin"
admin.site.index_title = "Administration Dashboard"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.action(description="Publish selected blogs")
def publish_blogs(modeladmin, request, queryset):
    for blog in queryset:
        old_status = blog.status
        blog.status = 'published'
        blog.save()

        if old_status != 'published' and blog.author.email:
            send_mail(
                'Your Blog Has Been Published',
                f'Congratulations {blog.author.username}, your blog "{blog.title}" has been approved and published on Blog Management System.',
                settings.DEFAULT_FROM_EMAIL,
                [blog.author.email],
                fail_silently=True,
            )


@admin.action(description="Move selected blogs to draft")
def draft_blogs(modeladmin, request, queryset):
    queryset.update(status='draft')


@admin.action(description="Archive selected blogs")
def archive_blogs(modeladmin, request, queryset):
    queryset.update(status='archived')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'image_preview',
        'title',
        'author',
        'category',
        'status',
        'is_featured',
        'views',
        'likes',
        'created_at',
    )

    list_filter = ('status', 'category', 'is_featured', 'created_at')

    search_fields = (
        'title',
        'short_description',
        'content',
        'author__username',
        'category__name',
    )

    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    readonly_fields = ('image_preview', 'views', 'likes', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    actions = [publish_blogs, draft_blogs, archive_blogs]

    fieldsets = (
        ('Basic Blog Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content Section', {
            'fields': ('image_preview', 'featured_image', 'short_description', 'content')
        }),
        ('Publishing Controls', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Performance Analytics', {
            'fields': ('views', 'likes')
        }),
        ('System Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width:80px;height:55px;object-fit:cover;border-radius:8px;" />',
                obj.featured_image.url
            )
        return "No Image"

    image_preview.short_description = "Image"

    def save_model(self, request, obj, form, change):
        old_status = None

        if change:
            old_obj = Blog.objects.get(pk=obj.pk)
            old_status = old_obj.status

        super().save_model(request, obj, form, change)

        if old_status != 'published' and obj.status == 'published':
            if obj.author.email:
                send_mail(
                    'Your Blog Has Been Published',
                    f'Congratulations {obj.author.username}, your blog "{obj.title}" has been approved and published on Blog Management System.',
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.author.email],
                    fail_silently=True,
                )


@admin.action(description="Approve selected comments")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Unapprove selected comments")
def unapprove_comments(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'name', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('comment', 'blog__title', 'user__username', 'name')
    list_editable = ('is_approved',)
    actions = [approve_comments, unapprove_comments]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_preview', 'user', 'website', 'linkedin')
    search_fields = ('user__username', 'bio', 'website')

    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:50%;" />',
                obj.profile_image.url
            )
        return "No Image"

    profile_preview.short_description = "Profile"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'name', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('blog__title', 'name', 'review')

    def rating_stars(self, obj):
        return "⭐" * obj.rating

    rating_stars.short_description = "Rating"


@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'user', 'created_at')
    search_fields = ('blog__title', 'user__username')
    list_filter = ('created_at',)