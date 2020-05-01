import datetime as dt
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required


def index(request):
        post_list = Post.objects.order_by('-pub_date').all()
        paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
        page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
        page = paginator.get_page(page_number) # получить записи с нужным смещением
        return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})

@login_required
def new_post(request):
    text_head = 'Добавить запись'
    text_button = 'Добавить'
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]
            image = form.cleaned_data["image"]
            Post.objects.create(text=text, group=group, author=request.user, image=image)
            return redirect('index')
            
        else:
            return render(request, 'new.html', {'form': form, 'text_head': text_head, 'text_button': text_button})
            
    else:
        form = PostForm(request.POST, files=request.FILES or None)
        return render(request, 'new.html', {'form': form, 'text_head': text_head, 'text_button': text_button})


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    profile = Post.objects.filter(author = post_author).order_by("-pub_date").all()
    paginator = Paginator(profile, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count = Post.objects.filter(author=post_author).count()
    if request.user.is_authenticated:
        follow_count = Follow.objects.filter(user=post_author).count()
        f_count = Follow.objects.filter(author=post_author).count()
        following = Follow.objects.filter(author=post_author, user=request.user).count()
        return render(request,'profile.html', {'post_author': post_author, 'paginator': paginator,'page': page, 'count': count, 'following' : following, 'follow_count' : follow_count, 'f_count' : f_count})
    else:
        return render(request,'profile.html', {'post_author': post_author, 'paginator': paginator,'page': page, 'count': count})
    
        
def post_view(request, username, post_id):
    post_author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=post_author, pk=post_id)
    count = Post.objects.filter(author=post_author).count()
    com = Comment.objects.filter(post=post)
    form = CommentForm()
    return render(request, "post.html", {'post_author': post_author, 'post': post,'count': count, "com" : com, "form" : form})


@login_required
def post_edit(request, username, post_id):
    text_head = 'Изменить запись'
    text_button = 'Сохранить'
    post_author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=post_author)
    if request.user == post_author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post) 
            if form.is_valid():
                form.save()
                return redirect(post_view, username, post_id)  
            else:
  
                return redirect(post_edit, username, post_id)
        else:
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            return render(request, 'new.html', {'form': form, 'post': post, 'text_head': text_head, 'text_button': text_button})
    else:
        return redirect(post_view, username, post_id)


def add_comment(request, username, post_id):
    post_author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=post_author, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            post = get_object_or_404(Post, author=post_author, id=post_id)
            author = get_object_or_404(User, username=request.user)
            Comment.objects.create(text=text, post=post, author=author)
            return redirect(post_view, username, post_id)
            
        else:
            form = CommentForm()
            return redirect(post_view, username, post_id)
            #return render(request, 'comments.html', {'form': form, 'post': post})
            
    else:
        form = CommentForm()
        return render(request, 'comments.html', {'form': form, 'post': post})
      

@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user).values_list("author_id", flat=True)
    count = Follow.objects.filter(user=request.user).count()
    post_list = Post.objects.filter(author_id__in=follow).order_by("-pub_date")
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.            
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'follow.html', {'page': page, 'paginator': paginator, 'count': count})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if not follow and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect(follow_index)


@login_required
def profile_unfollow(request, username):
    post_author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(user=request.user, author=post_author).delete()
    return redirect(index)


def page_not_found(request, exception):
        # Переменная exception содержит отладочную информацию, 
        # выводить её в шаблон пользователской страницы 404 мы не станем
        return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
        return render(request, "misc/500.html", status=500)




