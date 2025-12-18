from django.urls import path
from .views import (
    home,
    register,
    user_login,
    user_logout,
    product_detail,
    add_to_cart,
    view_cart,
    remove_cart,
    checkout,
    order_history,
    my_account,
    edit_profile,
    update_cart_quantity,
    order_detail

)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('product/<int:product_id>/', product_detail, name='product_detail'),

    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('remove/<int:item_id>/', remove_cart, name='remove_cart'),

    path('checkout/', checkout, name='checkout'),
    path('orders/', order_history, name='orders'),
    path('account/', my_account, name='my_account'),
    path('account/edit/', edit_profile, name='edit_profile'),
    path('cart/update/<int:cart_id>/', update_cart_quantity, name='update_cart_quantity'),
    path('orders/', order_history, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
]
