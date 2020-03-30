from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.db.models import Q
from .models import Post, Profile, Images
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.contrib import messages

# Create your views here.
def post_list(request):
    post_list = Post.published.all().order_by('-id')
    query = request.GET.get('q')
    if query:
        post_list = Post.published.filter(
            Q(title__icontains=query)|
            Q(author__username=query)|
            Q(body__icontains=query)
        )
    
    paginator = Paginator(post_list, 4)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)
    
    page_range = list(paginator.page_range)[start_index:end_index]
    # [1,2,3,4,5,6,7][0:7]


    context = {
        'posts': posts,
        'page_range': page_range,
    }
    return render(request, 'social/post_list.html', context)

def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index # 1
        end_index = start_index + end_index # 1+7 = 8 
    return (start_index, end_index)



def my_post(request):
    if not request.user.is_authenticated:
        raise Http404("Please login")
    post_list = Post.published.all().order_by('-id')
    post_list = post_list.filter(author=request.user)
    if not post_list:
        raise Http404("User does not exist")
    query = request.GET.get('q')
    if query:
        post_list = Post.published.filter(
            Q(title__icontains=query)|
            Q(author__username=query)|
            Q(body__icontains=query)
        )
    
    paginator = Paginator(post_list, 4)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)
    
    page_range = list(paginator.page_range)[start_index:end_index]
    # [1,2,3,4,5,6,7][0:7]


    context = {
        'posts': posts,
        'page_range': page_range,
    }
    return render(request, 'social/my_post.html', context)



def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
    is_liked = False
    is_favourite = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True
    
    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
            comment = Comment.objects.create(post=post, user=request.user, content=content, reply=comment_qs)
            comment.save()
            # return HttpResponseRedirect(post.get_absolute_url()) # No need of this while using ajax
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'is_liked': is_liked,
        'is_favourite': is_favourite,
        'total_likes': post.total_likes(),
        'comments': comments,
        'comment_form': comment_form,
    }
    if request.is_ajax():
        html = render_to_string('social/comments.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'social/post_detail.html', context)

def post_favourite_list(request):
    user = request.user
    favourite_post = user.favourite.all()
    context = {
        'favourite_post': favourite_post
    }
    return render(request, 'social/post_favourite_list.html', context)


def favourite_post(request, id):
    post = get_object_or_404(Post,  id=id)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())


def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    
    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('social/like_section.html', context, request=request)
        return JsonResponse({'form': html})



def post_create(request):
    ImageFormset = modelformset_factory(Images, fields=('image',), extra=4)
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        formset =ImageFormset(request.POST or None, request.FILES or None)
        # print(formset.cleaned_data)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            for f in formset:
                try:
                    photo = Images(post=post, image=f.cleaned_data['image'])
                    photo.save()
                except Exception as e:
                    break
            messages.success(request, 'Post has been successfully created!')
            return redirect('post_list')
    else:
        form = PostCreateForm()
        formset = ImageFormset(queryset=Images.objects.none())
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'social/post_create.html', context)



def post_edit(request, id):
    post = get_object_or_404(Post, id=id)
    ImageFormset = modelformset_factory(Images, fields=('image',), extra=4, max_num=4)
    if post.author != request.user:
        raise Http404()
    if request.method == 'POST':
        form = PostEditForm(request.POST or None, instance=post)
        formset =ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid() and formset.is_valid():
            form.save()
            print(formset.cleaned_data)
            for f in formset:
                if f.cleaned_data:
                    if f.cleaned_data['id'] is None:
                        photo = Images(post=post, image=f.cleaned_data['image'])
                        photo.save()
            messages.success(request, f"{post.title} has been successfully updated!")
            return HttpResponseRedirect(post.get_absolute_url())
            # return redirect("social:post_detail", id=instance.id)
    else:
        form = PostEditForm(instance=post)
        formset = ImageFormset(queryset=Images.objects.filter(post=post))
    
    context = {
        'form': form,
        'post': post,
        'formset': formset,
    }
    return render(request, 'social/post_edit.html', context)



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('post_list'))
                else:
                    return HttpResponse('User is not active')
            else:
                return HttpResponse('User is None')
    else:
        form = UserLoginForm()
    context = {
        'form': form,
    }
    return render(request, 'social/login.html', context)

def user_logout(request):
    logout(request)
    return redirect('post_list')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return redirect('user_login')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST or None, instance=request.user.profile, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('_social:my_profile'))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'social/edit_profile.html', context)

@login_required
def my_profile(request):
    return render(request, 'social/my_profile.html')

def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        raise Http404()
    post.delete()
    messages.warning(request, "Post has been successfully deleted!")
    return redirect('post_list')
