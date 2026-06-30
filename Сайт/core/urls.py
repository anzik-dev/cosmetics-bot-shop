"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from store import views as store_views
from django.conf import settings
from django.conf.urls.static import static
from store.views import toggle_bonus






urlpatterns = [
    path('admin/', admin.site.urls),
    path('',               store_views.index,           name='index'),
    path('shop/',          store_views.shop,            name='shop'),
    path('category/<str:category>/', store_views.category_view, name='category_view'),
    path('product/<int:product_id>/', store_views.product_detail, name='product_detail'),
    path('about/',         store_views.about,           name='about'),
    path('blog/',          store_views.blog,            name='blog'),
    path('cart/',          store_views.cart,            name='cart'),
    path('contact/',       store_views.contact,         name='contact'),
    path('cart/add/<int:product_id>/', store_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', store_views.update_cart, name='update_cart'),
    path('cart/ajax/update/<int:product_id>/', store_views.update_cart_ajax, name='update_cart_ajax'),
    path('accounts/', include('accounts.urls')),
    path('checkout/', store_views.checkout, name='checkout'),
    path('toggle-bonus/', store_views.toggle_bonus, name='toggle_bonus'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

