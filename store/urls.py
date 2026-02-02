from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),   

    path('login/', login_user, name='login'),
    path('register/',register_user, name='register'),
    path('logout/', logout_user, name='logout'),

    path('shop/', shop, name='shop'), 
    path('product/<int:id>/', product_detail, name='product_detail'),

    path('cart/', cart, name='cart'),
    path('add_cart/<int:product_id>/', add_cart, name='add_cart'),

    path('cart/add_item/<int:cart_item_id>/', add_cart_item, name='add_cart_item'),
    path('cart/remove/<int:cart_item_id>/', remove_cart, name='remove_cart'),
    path('cart/delete/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),

    path('checkout/', checkout, name='checkout'),
    path('place_order/', place_order, name='place_order'),

    path('my-orders/', my_orders, name='my_orders'),

    path('test/',test,name='test'),
]
