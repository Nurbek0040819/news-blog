from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.models import User
from app_news.models import News
from django.db.models import Q


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class AddNewsView(LoginRequiredMixin, CreateView):
    template_name = 'news/add_news.html'
    model = News
    success_url = reverse_lazy('home')
    fields = ['news_title', 'news_description', 'news_image', 'news_content', 'news_category']

    def form_valid(self, form):
        form.instance.news_author = self.request.user
        return super().form_valid(form)


class ListNewsView(ListView):
    template_name = 'news/list_news.html'
    model = News
    paginate_by = 6

    def get_queryset(self):
        queryset = News.objects.all().order_by('-news_pub_date')
        query = self.request.GET.get('q')
        if query:
            queryset = News.objects.filter(
                Q(news_title__icontains=query) |
                Q(news_content__icontains=query)
            ).order_by('-news_pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class DetailNewsView(DetailView):
    template_name = 'news/show_news.html'
    model = News

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = self.get_object()
        if self.request.user.is_authenticated:
            context['user_liked'] = news.likes.filter(id=self.request.user.id).exists()
            context['user_disliked'] = news.dislikes.filter(id=self.request.user.id).exists()
        else:
            context['user_liked'] = False
            context['user_disliked'] = False
        return context


class UpdateNewsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'news/update_news.html'
    model = News
    success_url = reverse_lazy('home')
    fields = ['news_title', 'news_description', 'news_image', 'news_content', 'news_category']

    def test_func(self):
        return self.request.user.is_superuser or self.get_object().news_author == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("Sizda yangilikni o'zgartirish uchun ruxsat yo'q.")


class DeleteNewsView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    success_url = reverse_lazy('home')
    template_name = 'news/delete_news.html'

    def test_func(self):
        return self.request.user.is_superuser or self.get_object().news_author == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("Sizda yangilikni o'chirish uchun ruxsat yo'q.")


@login_required
def like_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    if news.likes.filter(id=request.user.id).exists():
        news.likes.remove(request.user)
        liked = False
    else:
        news.likes.add(request.user)
        news.dislikes.remove(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes': news.total_likes(),
        'dislikes': news.total_dislikes(),
    })


@login_required
def dislike_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    if news.dislikes.filter(id=request.user.id).exists():
        news.dislikes.remove(request.user)
        disliked = False
    else:
        news.dislikes.add(request.user)
        news.likes.remove(request.user)
        disliked = True
    return JsonResponse({
        'disliked': disliked,
        'likes': news.total_likes(),
        'dislikes': news.total_dislikes(),
    })


def superuser_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                all_users_emails = User.objects.values_list('email', flat=True)
                for email in all_users_emails:
                    send_mail(
                        subject=request.POST['subject'],
                        message=request.POST['message'],
                        from_email=settings.EMAIL_HOST_USER or None,
                        recipient_list=[email]
                    )
                return HttpResponse("Successfully sent email to all users")
            except Exception as e:
                return HttpResponse(f"Something went wrong: {e}")
    return render(request, 'superuser.html')
