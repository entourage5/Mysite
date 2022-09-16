from django.shortcuts import render, get_object_or_404
from myblog.models import Post, Comment
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from myblog.forms import SigUpForm, SignInForm, FeedBackForm
from django.views import View
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from taggit.models import Tag
from myblog.forms import CommentForm


def index(request):
    template = 'myblog/home.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


class PostDetailView(View):

    def get(self, request, slug):
        post = get_object_or_404(Post, url=slug)
        common_tags = Post.tag.most_common()
        last_posts = Post.objects.all().order_by('-id')[:3]
        comment_form = CommentForm()
        context={
            'post': post,
            'common_tags': common_tags,
            'last_posts': last_posts,
            'comment_form': comment_form}
        return render(request, 'myblog/post_detail.html', context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = request.POST['text']
            username = request.user
            post = get_object_or_404(Post, url=slug)
            comment = Comment.objects.create(
                post=post, username=username, text=text)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, 'myblog/post_detail.html', context={
            'comment_form': comment_form
        })


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        context = {'form': form}
        return render(request, 'myblog/signup.html', context)

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'myblog/signup.html', context)


class SignInView(View):

    def get(self, request, *args, **kwargs):
        form = SignInForm
        context = {'form': form}
        return render(request, 'myblog/signin.html', context)

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'myblog/signin.html', context)


class FeedBackView(View):

    def get(self, request, *args, **kwargs):
        form = FeedBackForm
        context = {'form': form, 'title': 'Написать мне'}
        return render(request, 'myblog/contact.html', context)

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        context = {'form': form}
        if form.is_valid:
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(f'От {name} | {subject}', message, from_email,
                          ['vovan@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок!')
            return HttpResponseRedirect('succes')
        return render(request, 'myblog/contact.html', context)


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'myblog/success.html', context={
            'title': 'Спасибо'
        })


class SearchResultView(View):

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        results = ''
        if query:
            results = Post.objects.filter(Q(h1__icontains=query) |
                                          Q(content__icontains=query))
        paginator = Paginator(results, 3)
        page_num = request.GET.get('page')
        page_obj = paginator.get_page(page_num)
        return render(request, 'myblog/search.html', context={
            'title': 'Поиск',
            'results': page_obj,
            'count': paginator.count})


def tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tag=tag)
    common_tags = Post.tag.most_common()
    context = {'title': f'#ТЕГ {tag}', 'posts': posts,
               'common_tags': common_tags}
    return render(request, 'myblog/tag.html', context)
