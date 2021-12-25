from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from book_review_app import views

router = routers.DefaultRouter()

router.register(r'api/v1/register', views.CreateAuthorViewSet)
router.register(r'api/authors', views.AuthorViewSet) 
router.register(r'api/books', views.BookViewSet)
router.register(r'api/genres', views.GenreViewSet)
router.register(r'api/libraries', views.LibraryViewSet)


urlpatterns = [
    path('api/v1/api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/v1/api-token-deauth/', views.LogoutView.as_view(), name='api_token_deauth')
] + router.urls