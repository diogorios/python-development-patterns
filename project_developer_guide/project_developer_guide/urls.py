
from app_developer_guide import views
from django.urls import path

# Criar uma rota
# Criar uma view que a rota usará
# Nome da rota que liga ao HTML

urlpatterns = [
    path('',views.home,name='home'),
    path('users/',views.cadUser,name='caduser'),
    path('users/process/', views.process_cadUser, name='process_cadUser'),  
    path('users/login/',views.loginUser,name='loginuser'),
    path('users/processlogin/',views.process_login,name='process_login'),
    path('options',views.option,name='option'),
    path('options/category/',views.cadCategory,name='cadcategory'),
    path('categories/process/',views.process_cadCategory,name='process_cadCategory'),
    path('categories/', views.list_categories, name='list_categories'),
    path('excluir/<str:category_id>/', views.excluir_categoria, name='excluir_categoria'),
    path('options/pattern/',views.cadPattern,name='cadpattern'),
    path('patters/process/',views.process_cadPattern,name='process_cadPattern'),
    path('patterns/', views.list_patterns, name='list_patterns'),
    path('excluir_pattern/<str:pattern_id>/', views.excluir_padrao, name='excluir_padrao'),
]