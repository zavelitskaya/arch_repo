from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from rest_framework.views import APIView
from django.db import models
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import BusinessProcess
from .forms import BusinessProcessForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import IntegrationInteractionForm

from .models import (
    Team, BusinessProcess, Scenario, ScenarioStep,
    IntegrationService, IntegrationInteraction,
    System, Component, InfrastructureObject, ComponentInfrastructureLink
)
from .serializers import (
    TeamSerializer, BusinessProcessSerializer, ScenarioSerializer,
    IntegrationServiceSerializer, IntegrationInteractionSerializer,
    SystemSerializer, ComponentSerializer, InfrastructureObjectSerializer,
    ComponentInfrastructureLinkSerializer
)
from .forms import RegisterForm, LoginForm
from .decorators import unauthenticated_only


# ==================== HTML VIEWS (с защитой) ====================

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'repository/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processes_count'] = BusinessProcess.objects.count()
        context['systems_count'] = System.objects.count()
        context['interactions_count'] = IntegrationInteraction.objects.count()
        context['infra_count'] = InfrastructureObject.objects.count()
        
        # Последние бизнес-процессы
        context['recent_processes'] = BusinessProcess.objects.all().order_by('-created_at')[:5]
        
        # Последние интеграции (вместо компонентов)
        context['recent_interactions'] = IntegrationInteraction.objects.all().order_by('-created_at')[:5]
        
        return context


@method_decorator(login_required, name='dispatch')
class BusinessProcessListView(ListView):
    model = BusinessProcess
    template_name = 'repository/process_list.html'
    context_object_name = 'processes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(code__icontains=search_query) |
                models.Q(name__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(login_required, name='dispatch')
class BusinessProcessDetailView(DetailView):
    model = BusinessProcess
    template_name = 'repository/process_detail.html'
    context_object_name = 'process'


@method_decorator(login_required, name='dispatch')
class ComponentListView(ListView):
    model = Component
    template_name = 'repository/component_list.html'
    context_object_name = 'components'


@method_decorator(login_required, name='dispatch')
class ComponentDetailView(DetailView):
    model = Component
    template_name = 'repository/component_detail.html'
    context_object_name = 'component'


@method_decorator(login_required, name='dispatch')
class SystemListView(ListView):
    model = System
    template_name = 'repository/system_list.html'
    context_object_name = 'systems'


@method_decorator(login_required, name='dispatch')
class SystemDetailView(DetailView):
    model = System
    template_name = 'repository/system_detail.html'
    context_object_name = 'system'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.get_object()
        
        # Компоненты системы
        context['components'] = system.components.all()
        
        # Инфраструктура, привязанная к компонентам системы
        from .models import ComponentInfrastructureLink
        infra_links = ComponentInfrastructureLink.objects.filter(component__system=system)
        context['infra_objects'] = [link.infrastructure_object for link in infra_links]
        
        # Интеграции (входящие и исходящие)
        from .models import IntegrationInteraction
        interactions = IntegrationInteraction.objects.filter(
            source_component__system=system
        ) | IntegrationInteraction.objects.filter(
            target_component__system=system
        )
        context['interactions'] = interactions.distinct()
        
        # Получаем active_tab из GET-параметра
        context['active_tab'] = self.request.GET.get('tab', 'overview')
        
        return context


@method_decorator(login_required, name='dispatch')
class InteractionListView(ListView):
    model = IntegrationInteraction
    template_name = 'repository/interaction_list.html'
    context_object_name = 'interactions'


@method_decorator(login_required, name='dispatch')
class InteractionDetailView(DetailView):
    model = IntegrationInteraction
    template_name = 'repository/interaction_detail.html'
    context_object_name = 'interaction'


# ==================== AUTH VIEWS ====================

@unauthenticated_only
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('/')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = RegisterForm()
    
    return render(request, 'repository/register.html', {'form': form})


@unauthenticated_only
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                messages.success(request, f'С возвращением, {username}!')
                return redirect(next_url)
            else:
                messages.error(request, '❌ Неверный логин или пароль. Попробуйте ещё раз.')
        else:
            messages.error(request, '❌ Пожалуйста, заполните все поля корректно.')
    else:
        form = LoginForm()
    
    return render(request, 'repository/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('/accounts/login/')


# ==================== API VIEWS ====================

class DashboardAPIView(APIView):
    """API endpoint для дашборда"""
    def get(self, request):
        return Response({
            'business_processes': BusinessProcess.objects.count(),
            'components': Component.objects.count(),
            'systems': System.objects.count(),
            'interactions': IntegrationInteraction.objects.count(),
            'by_environment': {
                'dev': IntegrationInteraction.objects.filter(environment='dev').count(),
                'stage': IntegrationInteraction.objects.filter(environment='stage').count(),
                'prod': IntegrationInteraction.objects.filter(environment='prod').count(),
            }
        })


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class BusinessProcessViewSet(viewsets.ModelViewSet):
    queryset = BusinessProcess.objects.all()
    serializer_class = BusinessProcessSerializer
    
    @action(detail=True, methods=['get'])
    def full_hierarchy(self, request, pk=None):
        process = self.get_object()
        serializer = BusinessProcessSerializer(process)
        return Response(serializer.data)


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class IntegrationServiceViewSet(viewsets.ModelViewSet):
    queryset = IntegrationService.objects.all()
    serializer_class = IntegrationServiceSerializer


class IntegrationInteractionViewSet(viewsets.ModelViewSet):
    queryset = IntegrationInteraction.objects.all()
    serializer_class = IntegrationInteractionSerializer
    
    @action(detail=False, methods=['get'])
    def by_environment(self, request):
        env = request.query_params.get('env', 'prod')
        queryset = self.queryset.filter(environment=env)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    
    @action(detail=True, methods=['get'])
    def components_with_infra(self, request, pk=None):
        system = self.get_object()
        components = system.components.all()
        
        result = {
            'system': SystemSerializer(system).data,
            'components': []
        }
        
        for comp in components:
            infra_links = comp.infra_links.all()
            result['components'].append({
                'component': ComponentSerializer(comp).data,
                'infrastructure': ComponentInfrastructureLinkSerializer(infra_links, many=True).data
            })
        
        return Response(result)


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    
    @action(detail=True, methods=['get'])
    def dependencies(self, request, pk=None):
        component = self.get_object()
        incoming = IntegrationInteraction.objects.filter(target_component=component)
        outgoing = IntegrationInteraction.objects.filter(source_component=component)
        
        return Response({
            'component': ComponentSerializer(component).data,
            'depends_on': IntegrationInteractionSerializer(outgoing, many=True).data,
            'used_by': IntegrationInteractionSerializer(incoming, many=True).data
        })


class InfrastructureObjectViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureObject.objects.all()
    serializer_class = InfrastructureObjectSerializer

@method_decorator(login_required, name='dispatch')
class BusinessProcessCreateView(CreateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    success_url = reverse_lazy('process_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" успешно создан!')
        return super().form_valid(form)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import BusinessProcess
from .forms import BusinessProcessForm

@method_decorator(login_required, name='dispatch')
class BusinessProcessCreateView(CreateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    success_url = reverse_lazy('process_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" успешно создан!')
        return super().form_valid(form)
from .models import ProcessDocument

@method_decorator(login_required, name='dispatch')
class BusinessProcessCreateView(CreateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    success_url = reverse_lazy('process_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Обработка загруженных файлов
        files = self.request.FILES.getlist('documents')
        for file in files:
            ProcessDocument.objects.create(
                business_process=self.object,
                file=file,
                description='',
                uploaded_by=self.request.user.username
            )
        
        if files:
            messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" создан. Загружено файлов: {len(files)}')
        else:
            messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" успешно создан!')
        
        return response
    
@method_decorator(login_required, name='dispatch')
class BusinessProcessUpdateView(UpdateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    success_url = reverse_lazy('process_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)
    
from django.views.generic import DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Scenario, ScenarioStep, IntegrationInteraction

@method_decorator(login_required, name='dispatch')
class ScenarioDetailView(DetailView):
    model = Scenario
    template_name = 'repository/scenario_detail.html'
    context_object_name = 'scenario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario = self.get_object()
        
        # Получаем все шаги сценария
        steps = scenario.steps.all().order_by('step_order')
        
        # Формируем данные для визуализации
        nodes = []
        edges = []
        
        for step in steps:
            # Узел
            node = {
                'id': step.id,
                'label': f"Шаг {step.step_order}: {step.get_step_type_display()}",
                'type': step.step_type,
            }
            
            if step.step_type == 'ordinary' and step.interaction:
                node['title'] = step.interaction.name
            elif step.step_type == 'condition':
                node['title'] = step.condition_expression[:50]
            
            nodes.append(node)
            
            # Связи для обычных шагов (к следующему по порядку)
            if step.step_type == 'ordinary':
                next_step = steps.filter(step_order=step.step_order + 1).first()
                if next_step:
                    edges.append({'from': step.id, 'to': next_step.id})
            
            # Связи для ветвлений
            if step.step_type == 'condition':
                if step.true_next_step:
                    edges.append({'from': step.id, 'to': step.true_next_step.id, 'label': 'Истина'})
                if step.false_next_step:
                    edges.append({'from': step.id, 'to': step.false_next_step.id, 'label': 'Ложь'})
        
        context['nodes'] = nodes
        context['edges'] = edges
        context['steps'] = steps
        
        return context


@method_decorator(login_required, name='dispatch')
class ScenarioStepCreateView(CreateView):
    model = ScenarioStep
    fields = ['step_order', 'step_type', 'interaction', 'condition_expression', 'true_next_step', 'false_next_step']
    template_name = 'repository/step_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.scenario = Scenario.objects.get(pk=kwargs['scenario_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.scenario = self.scenario
        messages.success(self.request, 'Шаг добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('scenario_detail', kwargs={'pk': self.scenario.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scenario'] = self.scenario
        context['available_steps'] = self.scenario.steps.all().order_by('step_order')
        return context
    
import json
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Scenario

import json
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Scenario

@method_decorator(login_required, name='dispatch')
class ScenarioDetailView(DetailView):
    model = Scenario
    template_name = 'repository/scenario_detail.html'
    context_object_name = 'scenario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario = self.get_object()
        
        steps = scenario.steps.all().order_by('step_order')
        
        # Собираем уникальные системы и связи между ними
        systems = {}  # id -> {id, name, color}
        edges = []    # {from, to, label}
        
        for step in steps:
            if step.step_type == 'ordinary' and step.interaction:
                source_system = step.interaction.source_component.system
                target_system = step.interaction.target_component.system
                
                # Добавляем системы
                if source_system.id not in systems:
                    systems[source_system.id] = {
                        'id': source_system.id,
                        'name': source_system.name,
                    }
                if target_system.id not in systems:
                    systems[target_system.id] = {
                        'id': target_system.id,
                        'name': target_system.name,
                    }
                
                # Добавляем связь
                edges.append({
                    'from': source_system.id,
                    'to': target_system.id,
                    'label': step.interaction.name,
                    'step_order': step.step_order,
                    'protocol': step.interaction.protocol,
                })
        
        context['steps'] = steps
        context['systems_json'] = json.dumps(list(systems.values()), ensure_ascii=False)
        context['edges_json'] = json.dumps(edges, ensure_ascii=False)
        
        return context
    
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import ScenarioStep
from .forms import ScenarioStepForm

@method_decorator(login_required, name='dispatch')
class ScenarioStepCreateView(CreateView):
    model = ScenarioStep
    form_class = ScenarioStepForm
    template_name = 'repository/step_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.scenario = Scenario.objects.get(pk=kwargs['scenario_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['scenario'] = self.scenario
        return kwargs
    
    def form_valid(self, form):
        form.instance.scenario = self.scenario
        messages.success(self.request, f'Шаг {form.instance.step_order} добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('scenario_detail', kwargs={'pk': self.scenario.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scenario'] = self.scenario
        context['existing_steps'] = self.scenario.steps.all().order_by('step_order')
        return context


@method_decorator(login_required, name='dispatch')
class ScenarioStepUpdateView(UpdateView):
    model = ScenarioStep
    form_class = ScenarioStepForm
    template_name = 'repository/step_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['scenario'] = self.get_object().scenario
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'Шаг {form.instance.step_order} обновлён!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('scenario_detail', kwargs={'pk': self.get_object().scenario.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scenario'] = self.get_object().scenario
        context['existing_steps'] = self.get_object().scenario.steps.all().order_by('step_order')
        return context
    

@method_decorator(login_required, name='dispatch')
class InteractionListView(ListView):
    model = IntegrationInteraction
    template_name = 'repository/interaction_list.html'
    context_object_name = 'interactions'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        env_filter = self.request.GET.get('env', '')
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if env_filter:
            queryset = queryset.filter(environment=env_filter)
        
        return queryset.select_related('source_component__system', 'target_component__system')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_env'] = self.request.GET.get('env', '')
        return context


@method_decorator(login_required, name='dispatch')
class InteractionDetailView(DetailView):
    model = IntegrationInteraction
    template_name = 'repository/interaction_detail.html'
    context_object_name = 'interaction'

from .models import System

@method_decorator(login_required, name='dispatch')
class InteractionListView(ListView):
    model = IntegrationInteraction
    template_name = 'repository/interaction_list.html'
    context_object_name = 'interactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        env_filter = self.request.GET.get('env', '')
        system_filter = self.request.GET.get('system', '')
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if env_filter:
            queryset = queryset.filter(environment=env_filter)
        if system_filter:
            queryset = queryset.filter(
                models.Q(source_component__system_id=system_filter) |
                models.Q(target_component__system_id=system_filter)
            )
        
        return queryset.select_related('source_component__system', 'target_component__system')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_env'] = self.request.GET.get('env', '')
        context['current_system'] = self.request.GET.get('system', '')
        context['systems'] = System.objects.all().order_by('name')
        return context
    
@method_decorator(login_required, name='dispatch')
class InteractionCreateView(CreateView):
    model = IntegrationInteraction
    form_class = IntegrationInteractionForm
    template_name = 'repository/interaction_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграция "{form.instance.name}" успешно создана!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('interaction_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class InteractionUpdateView(UpdateView):
    model = IntegrationInteraction
    form_class = IntegrationInteractionForm
    template_name = 'repository/interaction_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграция "{form.instance.name}" успешно обновлена!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('interaction_detail', kwargs={'pk': self.object.pk})
    
from .forms import ScenarioForm

@method_decorator(login_required, name='dispatch')
class ScenarioUpdateView(UpdateView):
    model = Scenario
    form_class = ScenarioForm
    template_name = 'repository/scenario_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Сценарий "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('scenario_detail', kwargs={'pk': self.object.pk})