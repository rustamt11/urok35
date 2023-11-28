from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView

from django.contrib.auth.decorators import login_required
from .forms import CommentModelForm
from .models import *


class ProductListView(ListView):
    template_name = 'app/product_list.html'
    model = Product


def logout_user(request):
    logout(request)
    return redirect('product_list')


class RegisterUserView(CreateView):
    template_name = 'app/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('product_list')

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.POST.get('username'))
        Cart.objects.create(user=user)
        return redirect('product_list')


class UserLoginView(LoginView):
    template_name = 'app/login.html'
    form_class = AuthenticationForm
    next_page = reverse_lazy('product_list')


class UserProfileView(ListView):
    template_name = 'app/profile.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.get(user=user).product_list.all()


class CartView(ListView):
    template_name = 'app/cart.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.get(user=user).product_list.all()


def add_product(request, product_id):
    if request.method == 'GET':
        Cart.objects.get(user=request.user).product_list.add(
            Product.objects.get(id=product_id)
        )
    return redirect('product_list')


def remove_from_cart(request, slug):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)
    cart.product_list.remove(product)
    return redirect('cart')


def buy_products(request):
    if request.method == 'GET':
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        bh = BuyHistory.objects.create(user=user)
        bh.product_list.set(cart.product_list.all())
        cart.product_list.clear()
        return redirect('cart')


class BuyHistoryListView(ListView):
    template_name = 'app/buy_history.html'
    context_object_name = 'history_list'

    def get_queryset(self):
        user = self.request.user
        return BuyHistory.objects.filter(user=user)


class ProductDetailView(DetailView):
    template_name = 'app/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentModelForm()

        comments = Comment.objects.filter(product=self.get_object())
        context['comment_list'] = comments

        return context


def add_comment(request, slug):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product, slug=slug)
        form = CommentModelForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.product = product
            comment.save()
            return redirect('product_detail', slug=slug)


def like_product(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    content_type = ContentType.objects.get_for_model(product)

    Dislike.objects.filter(
        content_type=content_type, object_id=product.id, user=user).delete()

    Like.objects.get_or_create(
        content_type=content_type, object_id=product.id, user=user)

    return redirect('product_list')


def like_comment(request, pk):
    user = request.user
    comment = get_object_or_404(Comment, pk=pk)
    content_type = ContentType.objects.get_for_model(comment)

    Dislike.objects.filter(
        content_type=content_type, object_id=comment.id, user=user).delete()

    Like.objects.get_or_create(
        content_type=content_type, object_id=comment.id, user=user)

    slug = comment.product.slug
    return redirect('product_detail', slug=slug)


def dislike_product(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    content_type = ContentType.objects.get_for_model(product)

    Like.objects.filter(
        content_type=content_type, object_id=product.id, user=user).delete()

    Dislike.objects.get_or_create(
        content_type=content_type, object_id=product.id, user=user)

    return redirect('product_list')


def dislike_comment(request, pk):
    user = request.user
    comment = get_object_or_404(Comment, pk=pk)
    content_type = ContentType.objects.get_for_model(comment)

    Like.objects.filter(
        content_type=content_type, object_id=comment.id, user=user).delete()

    Dislike.objects.get_or_create(
        content_type=content_type, object_id=comment.id, user=user)

    slug = comment.product.slug
    return redirect('product_detail', slug=slug)