from django.db import models
from django.db.models.functions import math
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
import numpy as np
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from time import strftime, gmtime
from PIL import Image
from django.db.models.signals import post_save
from django.conf import settings


class MyModelName(models.Model):
    """A typical class defining a model, derived from the Model class."""

    # Fields
    my_field_name = models.CharField(
        max_length=20, help_text='Enter field documentation')
    

    # Metadata
    class Meta:
        ordering = ['-my_field_name']

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.my_field_name


class Category(models.Model):
    name_category = models.CharField(max_length=20, null=True, help_text=(
        'Enter a song category (e.g. Sad love)'))
    thumbnail = models.ImageField(upload_to="thumbnails", blank=False, default="default.jpeg")

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])

    def __str__(self):
        return self.name_category
    thumbnail = models.ImageField(upload_to="genres", default="default.jpeg")


class Album(models.Model):
    name_album = models.CharField(max_length=50)

    def get_absolute_url(self):
        return reverse('album-detail', args=[str(self.id)])

    def __str__(self):
        return self.name_album


class Lyric(models.Model):
    content = models.CharField(max_length=1000, null=True)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    lyric_status = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(
        'Artist', help_text='Select song for this artist')
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True)
    album = models.ManyToManyField(
        'Album', help_text='Select album for this song')
    hot = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="thumbnails", blank=False, default="default.jpg")
    song = models.FileField(upload_to="song_directory_path", default="default.mp3")
    playtime = models.CharField(max_length=10, default="0.00")
    size = models.IntegerField(default=0)

    @property
    def duration(self):
        return str(strftime('%H:%M:%S', gmtime(float(self.playtime))))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('song-detail', args=[str(self.id)])

    def display_category(self):
        return ', '.join(category.name for category in self.category.all()[:5])

    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(list(all_ratings))

    def get_lyric(self):
         return Lyric.objects.filter(song=self)

class Artist(models.Model):
    name_artist = models.CharField(max_length=50)
    birthday = models.DateField(null=True, blank=True)
    biography = models.CharField(max_length=400, null=True, help_text=(
        'Enter your biography '))
    def get_absolute_url(self):
        return reverse('artist-detail', args=[str(self.id)])

    def __str__(self):
        return self.name_artist

    @property
    def file_size(self):
        if self.size == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(self.size, 1024)))
        p = math.pow(1024, i)
        s = round(self.size / p, 2)
        return "%s %s" % (s, size_name[i])


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20)
    password = models.CharField(None, max_length=128)

    email = models.EmailField(
        verbose_name='email address', max_length=255, unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    # notice the absence of a "Password field", that is built in.
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default# .

    def __str__(self):
        return self.username

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    def get_followers(self):
        return Follow.objects.filter(following=self).count()

    def get_followings(self):
        return Follow.objects.filter(follower=self).count()

    def list_follower(self):
        followers = Follow.objects.filter(following=self)
        users = list()
        for follower in followers:
            users.append(User.objects.get(email=follower.follower))
        return users

    def list_following(self):
        followings = Follow.objects.filter(follower=self)
        users = list()
        for following in followings:
            users.append(User.objects.get(email=following.following))
        return users

    def list_favorite(self):
         user_favorite = Favorite.objects.filter(user_favorite=self)
         songs = list()
         for song in user_favorite:
            songs.append(Song.objects.get(title=song.song_favorite))
         return songs


class Comment(models.Model):
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    # comment = models.ForeignKey('Comment', max_length=200, on_delete=models.SET_NULL)
    text = models.TextField()
    date_comment = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey('User', on_delete=models.CASCADE)



class Review(models.Model):
    content_review = models.CharField(max_length=1000)
    song_review = models.ForeignKey('Song', on_delete=models.CASCADE)
    user_review = models.ForeignKey('User', on_delete=models.CASCADE)
    date_review = models.DateTimeField(default=timezone.now)
    RATING_CHOICES = (
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    )
    rating = models.IntegerField(choices=RATING_CHOICES)

    def __str__(self):
        return self.content_review

    @property
    def actual_rating(self):
        list_of_stars = []
        for star in range(self.rating):
            list_of_stars.append(star)
        return list_of_stars

    @property
    def hidden_rating(self):
        list_of_stars = []
        for star in range(5 - self.rating):
            list_of_stars.append(star)
        return list_of_stars


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('follower', 'following')

    def __unicode__(self):
        return u'%s follows %s' % (self.follower, self.following)

class Favorite(models.Model):
    favorite_name = models.CharField(max_length=50)
    user_favorite = models.ForeignKey('User',related_name='user_favorite', on_delete=models.CASCADE)
    song_favorite = models.ForeignKey('Song', related_name='song_favorite',on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_favorite', 'song_favorite')

    def __unicode__(self):
        return u'%s follows %s' % (self.user_favorite, self.song_favorite)

class Profile (models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='avatar.jpg',upload_to='profile_pics', null=True)

    def __str__(self):
        return f'{self.user.username}Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        return reverse('follow', args=[str(self.user.id)])


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
