from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, DeleteView, ListView
from .models import Song, Artist, Category, Album, Review, User, Profile
# from utils.song_utils import generate_key
from .forms import UserUpdateForm, ProfileUpdateForm, LyricAddForm, ReviewForm, SongUploadForm
from .forms import RegisterForm
from tinytag import TinyTag
from django.http import  HttpResponseRedirect
from tinytag import TinyTag
from django.views.generic.list import BaseListView
from .models import *
# from utils.song_utils import generate_key
from .forms import UserUpdateForm, ProfileUpdateForm


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
# from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import  get_object_or_404
import ssl,smtplib
import environ
import os
# from django.utils.translation import ugettext_lazy as _

env = environ.Env()
# reading .env file
environ.Env.read_env()


def index(request):
    a = Song.objects.all()
    context = {
        'artists' : Artist.objects.all()[:6],
        'genres': Category.objects.all()[:6],
        'latest_songs': Song.objects.all(),
        'latest_songs_2': Song.objects.all(),
        # 'latest_songs': Song.objects.all()[len(a)-3:len(a)],
        # 'latest_songs_2': Song.objects.all()[len(a)-5:len(a)],
    }
    return render(request, "index.html", context)


class CategoryListView(ListView):
    model = Category


class CategoryDetailView(DetailView):
    model = Category

class SongListView(ListView):
    model = Song


class ArtistListView(ListView):
    model = Artist


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Successful!!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user': request.user,
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'registration/profile.html', context)


class ArtistDetailView(DetailView):
    model = Artist


class HotSongListView(ListView):
    model = Song
    template_name = 'myalbums/hot_music.html'
    context_object_name = 'songs'

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')
        data = {'username':username,'email': email, 'password1': password1, 'password1': password2}
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(password1)
            user.active = False
            user.save()
            form.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            # subject = 'Activate your blog account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # 'token':account_activation_token.make_token(user),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email], from_email=settings.EMAIL_HOST_USER
            )
            email.content_subtype = "html" 
            email.send()
            # send_mail('check', 'hello','nguyen.thi.dungb@sun-asterisk.com',['tran.van.thongb@sun-asterisk.com'],fail_silently=False,)
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# user = get_object_or_404(User, pk=uid)
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class SearchSongListView(ListView):
    # template_name = 'myalbums/song_detail.html'
    model = Song
    def get_queryset(self):
        query = self.request.GET.get('search')
        if query :
            return  Song.objects.filter(title__icontains=query)
        else :
            return  Song.objects.all()

class StationListView(ListView):
    model = User
    template_name = 'myalbums/user_list.html'

@login_required()
def follow(request, pk):
    if request.method == 'GET':
        user = request.user
        to_user = get_object_or_404(User, pk=pk)
        is_followed = 0

        try:
            followed = Follow.objects.get(follower=user, following=to_user)
            if followed:
                is_followed = 1
        except:
            pass

        context = {
            'user': user,
            'to_user': to_user,
            'is_followed': is_followed,
        }
        return render(request, 'myalbums/user_detail.html', context=context)
    elif request.method == 'POST':
        user = request.user
        to_user = get_object_or_404(User, pk=pk)

        try:
            followed = Follow.objects.get(follower=user, following=to_user)
            if followed:
                followed.delete()
                content = ' Unfollowed  : ' + to_user.username
                activity = Activity(user=user, activity_type='unfollow', activity=content)
                activity.save()
        except:
            follow = Follow(follower=user, following=to_user)
            follow.save()
            content = ' Now following  : ' + to_user.username
            activity = Activity(user=user, activity_type='follow', activity=content)
            activity.save()

        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)


@login_required()
def favorite(request, pk):
    if request.method == 'GET':
        user = request.user
        favorite = get_object_or_404(Song, pk=pk)
        is_favorite = 0

        try:
            favorited = Favorite.objects.get(user_favorite = user, song_favorite = favorite)
            if favorited:
                is_favorite= 1
        except:
            pass

        context = {
            'user': user,
            'favorite': favorite,
            'is_favorite': is_favorite,
        }
        return render(request, 'myalbums/song_detail.html', context=context)
    elif request.method == 'POST':
        user = request.user
        favorite = get_object_or_404(Song, pk=pk)

        try:
            favorited = Favorite.objects.get(user_favorite = user, song_favorite = favorite)
            if favorited:
                favorited.delete()
                content = ' Disliked : ' + favorite.title
                activity = Activity(user=user, activity_type='unfavorite', activity=content)
                activity.save()
        except:
            favorited = Favorite(user_favorite = user, song_favorite = favorite)
            favorited.save()
            content = ' Liked : ' + favorite.title
            activity = Activity(user = user, activity_type='favorite', activity= content)
            activity.save()
        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)

class FavoriteListView(ListView):
    model = Song
    template_name = 'myalbums/favorite.html'

def addlyric(request, pk):
    user = request.user
    song = get_object_or_404(Song, pk=pk)
    # content = Lyric.content
    form = LyricAddForm()
    context = {
        'user': user,
        'song': song,
        # 'content': content,
        'form': form,
    }
    if request.method == 'POST':
            form = LyricAddForm(request.POST, initial={'user': user, 'song': song})
            if form.is_valid():
                form.save()
                return redirect('song-detail', pk)

    return render(request, 'myalbums/lyric_add.html', context)

@login_required
def ReviewAdd(request, pk):
    user = request.user
    song = get_object_or_404(Song, pk=pk)
    form = ReviewForm()
    context = {
        'user': user,
        'song': song,
        'form': form,
    }
    if request.method == 'POST':
        form = ReviewForm(request.POST, initial={'user': user, 'song': song})
        if form.is_valid():
            form.save()
            content = ' had reviewed : ' + song.title
            activity = Activity(user=user, activity_type='review', activity = content)
            activity.save()
            return redirect('song-detail',pk)
    return render(request, 'myalbums/review_form.html', context)


# @login_required
# def upload(request):
#     user = request.user
#     form = SongUploadForm()
#     context = {
#         'user': user,
#         'form': form,
#     }
#     if request.method == 'POST':
#         form = ReviewForm(request.POST, initial={'user': user})
#         if form.is_valid():
#             form.save()
#             return redirect('song')
#     return render(request, 'myalbums/create.html', context)


class SongUploadView(CreateView):
    form_class = SongUploadForm
    template_name = "myalbums/create.html"

    @method_decorator(login_required(login_url=reverse_lazy('index')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SongUploadView, self).get_context_data(**kwargs)
        context['artists'] = Artist.objects.all()
        context['category'] = Category.objects.all()
        return context


    def post(self, request, *args, **kwargs):

        form = self.get_form()
        print(form)
        if form.is_valid():

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=200)

    def form_valid(self, form):
        song = TinyTag.get(self.request.FILES['song'].file.name)
        form.instance.playtime = song.duration
        form.instance.size = song.filesize
        artists = []
        for a in self.request.POST.getlist('artists[]'):
            try:
                artists.append(int(a))
            except:
                artist = Artist.objects.create(name=a)
                artists.append(artist)
        form.save()
        form.instance.artist.set(artists)
        form.save()
        data = {
            'status': True,
            'message': "Successfully submitted form data.",
            'redirect': reverse_lazy('song-detail', kwargs={'pk': form.instance.id})
        }

        return JsonResponse(data)   

class ActivityListView(ListView):
    template_name = 'myalbums/activity_list.html'
    model = Activity
    # paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ActivityListView, self).get_context_data(**kwargs)
        followings = Follow.objects.filter(follower=self.request.user)
        user_list = [self.request.user]
        for following in followings:
            user_list.append(following.following)
        activity_list = Activity.objects.filter(user__in=user_list).order_by('-id')
        context.update({
            'history': activity_list
        })
        return context

