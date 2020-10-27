from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# URLの全体設計
urlpatterns = [
    path('landing/', include('landing.urls')),
    path('accounts/', include('allauth.urls')),
    path('transaction/', include('transaction.urls')),
    path('atm/', include('atm.urls')),
    path('api/', include('bankapi.urls')),
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
]

# メディアファイル公開用のURL設定
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
