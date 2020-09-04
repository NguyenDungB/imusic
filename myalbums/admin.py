from django.contrib import admin
import numpy as np

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import *


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'category', 'song', 'hot')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name_category','thumbnail']
#     inlines = [SongInline]


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    fields = ['name_album']
#     inlines = [SongInline]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    #     list_display = ('name_artist', 'birthday')
    fields = ['name_artist']

# @admin.register(Favourite)
# @admin.register(Follower)
# @admin.register(Comment)
# @admin.register(Lyric)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('song_review', 'user_review',
                    'content_review', 'date_review', 'rating')


# admin.site.register(Profile)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ('id','user')

admin.site.register(Follow)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
   fields = ['user_favorite', 'song_favorite']


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin','username')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password','username')}),
        ('Permissions', {'fields': ('admin','staff','active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

admin.site.register(Lyric)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

admin.site.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('song_review', 'user_review',
#                     'content_review', 'date_review', 'rating')
