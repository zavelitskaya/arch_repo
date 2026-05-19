from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from repository import views

router = DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'processes', views.BusinessProcessViewSet)
router.register(r'scenarios', views.ScenarioViewSet)
router.register(r'services', views.IntegrationServiceViewSet)
router.register(r'flows', views.IntegrationFlowViewSet)
router.register(r'systems', views.SystemViewSet)
router.register(r'components', views.ComponentViewSet)
router.register(r'infrastructure', views.InfrastructureObjectViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # HTML страницы
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('processes/', views.BusinessProcessListView.as_view(), name='process_list'),
    path('processes/create/', views.BusinessProcessCreateView.as_view(), name='process_create'),
    path('processes/<int:pk>/', views.BusinessProcessDetailView.as_view(), name='process_detail'),
    path('processes/<int:pk>/edit/', views.BusinessProcessUpdateView.as_view(), name='process_edit'),
    
    path('systems/', views.SystemListView.as_view(), name='system_list'),
    path('systems/<int:pk>/', views.SystemDetailView.as_view(), name='system_detail'),
    
    path('scenarios/<int:pk>/', views.ScenarioDetailView.as_view(), name='scenario_detail'),
    path('scenarios/<int:pk>/edit/', views.ScenarioUpdateView.as_view(), name='scenario_edit'),
    path('scenarios/<int:scenario_pk>/steps/create/', views.ScenarioStepCreateView.as_view(), name='step_create'),
    path('steps/<int:pk>/edit/', views.ScenarioStepUpdateView.as_view(), name='step_edit'),
    
    path('interactions/', views.InteractionListView.as_view(), name='interaction_list'),
    path('interactions/create/', views.InteractionCreateView.as_view(), name='interaction_create'),
    path('interactions/<int:pk>/', views.InteractionDetailView.as_view(), name='interaction_detail'),
    path('interactions/<int:pk>/edit/', views.InteractionUpdateView.as_view(), name='interaction_edit'),
    
    # API
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='api_dashboard'),
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentication
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
# Интеграционные сервисы
path('services/', views.IntegrationServiceListView.as_view(), name='service_list'),
path('services/<int:pk>/', views.IntegrationServiceDetailView.as_view(), name='service_detail'),
path('services/create/', views.IntegrationServiceCreateView.as_view(), name='service_create'),
path('services/<int:pk>/edit/', views.IntegrationServiceUpdateView.as_view(), name='service_edit'),
]

# Для медиафайлов в разработке
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)