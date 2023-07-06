from django.urls import path
from .views import PostCreateView, PostListView, PostDeleteView, PostUpdateView, PostDetailView, response_accept, \
    user_response, ResponseCreateView, ResponseListView, ResponseUpdateView, ResponseDeleteView, RegisterUser, \
    onetimecodeinput, activation, LoginUser, logout_user, UserDataUpdate

urlpatterns = [
    # post
    path('post/', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post_create/', PostCreateView.as_view(), name='post_create'),
    path('post_update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('post_delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),

    # response
    path('response/', ResponseListView.as_view(), name='response_list'),
    path('response_create/', ResponseCreateView.as_view(), name='response_create'),
    path('response_update/<int:pk>/', ResponseUpdateView.as_view(), name='response_update'),
    path('response_delete/<int:pk>/', ResponseDeleteView.as_view(), name='response_delete'),
    path('user_response/', user_response, name='user_response'),
    path('response_accept/<int:resp_id>/', response_accept, name='response_accept'),

    # auth
    path('register/', RegisterUser.as_view(), name='register'),
    path('onetimecodeinput/', onetimecodeinput, name='onetimecodeinput'),
    path('activation/', activation, name='activation'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('user_edit/', UserDataUpdate.as_view(), name='user_edit'),

]
