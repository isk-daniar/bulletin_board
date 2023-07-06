from random import SystemRandom

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from .forms import BaseRegisterForm, UserDataForm, ResponseForm, PostForm
from .models import Post, Category, Response, EmailKey
from .filters import ResponseFilter


paginator_items_count = 10

# Post
class PostListView(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'massage_boards/post_list.html'
    context_object_name = 'posts'
    paginate_by = paginator_items_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat'] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'massage_boards/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resp'] = Response.objects.filter(post=self.object)
        context['cats'] = Category.objects.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'massage_boards/post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание объявления:'
        return context

    def get_success_url(self):
        return reverse('post_detail', args=(self.object.id))

class PostUpdateView(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'massage_boards/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование объявления:'
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_id != self.request.user:
            return HttpResponseForbidden()
        return super(PostUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('post_update', args=(self.object.id,))


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'massage_boards/post_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_id != self.request.user:
            return HttpResponseForbidden()
        return super(PostDeleteView, self).dispatch(request, *args, **kwargs)


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
        else:
            post.likes.add(user)

        likes_count = post.likes.count()
        return JsonResponse({'likes_count': likes_count})

# Response
class ResponseListView(ListView):
    model = Response
    ordering = '-created_at'
    template_name = 'massage_boards/response_list.html'
    context_object_name = 'responses'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ResponseFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class ResponseCreateView(LoginRequiredMixin, CreateView):
    form_class = ResponseForm
    model = Response
    template_name = 'massage_boards/response_create.html'

    def form_valid(self, form):
        resp = form.save(commit=False)
        resp.user_id = self.request.user
        post = Post.objects.get(pk=self.kwargs['post'])
        resp.post = post
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление отклика:'
        return context

    def get_success_url(self):
        return reverse('post_detail', args=(self.object.post.pk,))


class ResponseUpdateView(UpdateView):
    form_class = ResponseForm
    model = Response
    template_name = 'massage_boards/response_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование отклика:'
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_id != self.request.user:
            return HttpResponseForbidden()
        return super(ResponseUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('response_update', args=(self.object.id,))


class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = Response
    template_name = 'massage_boards/response_delete.html'
    success_url = reverse_lazy('user_response')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post.user_id != self.request.user:
            return HttpResponseForbidden()
        return super(ResponseDeleteView, self).dispatch(request, *args, **kwargs)


# Auth
class RegisterUser(CreateView):
    form_class = BaseRegisterForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('activation')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()
        # создаем ключ
        new_random_obj = SystemRandom()
        onetime_key = EmailKey.objects.create(key=new_random_obj.randrange(100000, 999999), user_id=user)
        # отправляем письмо на почту
        send_mail(
            subject='Код для активации учетной записи (BulletinBoard)',
            message=f'Одноразовый код для активации учетной записи: {onetime_key.key}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'user/login.html'


class UserDataUpdate(LoginRequiredMixin, UpdateView):
    form_class = UserDataForm
    model = User
    template_name = 'user/user_edit.html'
    success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование данных пользователя:'
        return context

    def get_object(self):
        return self.request.user


def logout_user(request):
    logout(request)
    return redirect('login')

def onetimecodeinput(request):
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        if EmailKey.objects.filter(key=code, user_id__username=username):
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('login')
        else:
            return HttpResponse('Неверное имя пользователя и/или одноразовый код.')
    else:
        return render(request, 'user/activation.html')


def activation(request):
    return render(request, 'user/activation.html')


def user_response(request):
    user = request.user
    queryset = Response.objects.filter(post__in=user.post_set.all())
    filterset = ResponseFilter(request.GET, my_user_id=user.pk, queryset=queryset)
    context = {
        'responses': filterset.qs,
        'filterset': filterset,
    }
    return render(request, 'massage_boards/search.html', context=context)


@login_required
def response_accept(request, resp_id):
    resp = Response.objects.get(pk=resp_id)
    user = User.objects.get(pk=resp.user_id.pk)
    # отправляем письмо на почту
    send_mail(
        subject='Ваш отклик принят.',
        message=f'Пользователь {request.user} принял ваш отклик!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return HttpResponse('Подтверждение принятия отклика - письмо пользователю, оставившему отклик, отправлено!')
