from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from repository import views
from repository import views as repo_views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'processes', views.BusinessProcessViewSet)
router.register(r'scenarios', views.ScenarioViewSet)
router.register(r'services', views.IntegrationServiceViewSet)
router.register(r'interactions', views.IntegrationInteractionViewSet)
router.register(r'systems', views.SystemViewSet)
router.register(r'components', views.ComponentViewSet)
router.register(r'infrastructure', views.InfrastructureObjectViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
        # Authentication
    path('accounts/register/', repo_views.register_view, name='register'),
    path('accounts/login/', repo_views.login_view, name='login'),
    path('accounts/logout/', repo_views.logout_view, name='logout'),
    # HTML страницы
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('processes/', views.BusinessProcessListView.as_view(), name='process_list'),
    path('processes/<int:pk>/', views.BusinessProcessDetailView.as_view(), name='process_detail'),
    path('components/', views.ComponentListView.as_view(), name='component_list'),
    path('components/<int:pk>/', views.ComponentDetailView.as_view(), name='component_detail'),
    path('systems/', views.SystemListView.as_view(), name='system_list'),
    path('systems/<int:pk>/', views.SystemDetailView.as_view(), name='system_detail'),
    path('interactions/', views.InteractionListView.as_view(), name='interaction_list'),
    path('interactions/<int:pk>/', views.InteractionDetailView.as_view(), name='interaction_detail'),
    
    # API
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='api_dashboard'),
    path('api-auth/', include('rest_framework.urls')),

    path('processes/create/', views.BusinessProcessCreateView.as_view(), name='process_create'),
    path('processes/<int:pk>/edit/', views.BusinessProcessUpdateView.as_view(), name='process_edit'),
    path('scenarios/<int:pk>/', views.ScenarioDetailView.as_view(), name='scenario_detail'),
    path('scenarios/<int:scenario_pk>/steps/create/', views.ScenarioStepCreateView.as_view(), name='step_create'),
    path('scenarios/<int:scenario_pk>/steps/create/', views.ScenarioStepCreateView.as_view(), name='step_create'),
    path('steps/<int:pk>/edit/', views.ScenarioStepUpdateView.as_view(), name='step_edit'),
    path('interactions/', views.InteractionListView.as_view(), name='interaction_list'),
    path('interactions/<int:pk>/', views.InteractionDetailView.as_view(), name='interaction_detail'),
    path('interactions/create/', views.InteractionCreateView.as_view(), name='interaction_create'),
    path('interactions/<int:pk>/edit/', views.InteractionUpdateView.as_view(), name='interaction_edit'),
    path('scenarios/<int:pk>/edit/', views.ScenarioUpdateView.as_view(), name='scenario_edit'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)