from django.contrib import admin
from social.models import Post, Profile, Images, Comment
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status')
    list_filter = ('status', 'created', 'updated')
    search_fields = ('author__username', 'title')
    prepopulated_fields = {'slug':('title',)}
    list_editable = ('status',)
    date_hierarchy = ('created')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dob', 'photo')

class ImagesAdmin(admin.ModelAdmin):
    list_display = ('post', 'image')



admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Comment)
