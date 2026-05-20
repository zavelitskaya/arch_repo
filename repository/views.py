import json
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from rest_framework.views import APIView
from django.urls import reverse_lazy

from .models import (
    Team, BusinessProcess, ProcessDocument, Scenario, ScenarioStep,
    IntegrationService, IntegrationFlow, System, Component, 
    InfrastructureObject, ComponentInfrastructureLink
)
from .serializers import (
    TeamSerializer, BusinessProcessSerializer, ScenarioSerializer,
    IntegrationServiceSerializer, IntegrationFlowSerializer,
    SystemSerializer, ComponentSerializer, 
    InfrastructureObjectSerializer, ComponentInfrastructureLinkSerializer
)
from .forms import (
    RegisterForm, LoginForm, BusinessProcessForm, ScenarioForm, 
    ScenarioStepForm, IntegrationServiceForm, IntegrationFlowForm
)
from .decorators import unauthenticated_only


# ==================== HTML VIEWS ====================

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'repository/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processes_count'] = BusinessProcess.objects.count()
        context['systems_count'] = System.objects.count()
        context['interactions_count'] = IntegrationFlow.objects.count()
        context['infra_count'] = InfrastructureObject.objects.count()
        context['recent_processes'] = BusinessProcess.objects.all().order_by('-created_at')[:5]
        context['recent_interactions'] = IntegrationFlow.objects.all().order_by('-created_at')[:5]
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
class BusinessProcessCreateView(CreateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
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
    
    def get_success_url(self):
        return reverse_lazy('process_list')


@method_decorator(login_required, name='dispatch')
class BusinessProcessUpdateView(UpdateView):
    model = BusinessProcess
    form_class = BusinessProcessForm
    template_name = 'repository/process_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Бизнес-процесс "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('process_list')


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
        context['components'] = system.components.all()
        
        infra_links = ComponentInfrastructureLink.objects.filter(component__system=system)
        context['infra_objects'] = [link.infrastructure_object for link in infra_links]
        
        context['active_tab'] = self.request.GET.get('tab', 'overview')
        return context


import json

@method_decorator(login_required, name='dispatch')
class ScenarioDetailView(DetailView):
    model = Scenario
    template_name = 'repository/scenario_detail.html'
    context_object_name = 'scenario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scenario = self.get_object()
        steps = scenario.steps.all().order_by('step_order')
        
        systems = {}
        edges = []
        
        for step in steps:
            if step.flow:
                source_system = step.flow.source_system
                target_system = step.flow.target_system
                
                if source_system.id not in systems:
                    systems[source_system.id] = {'id': source_system.id, 'name': source_system.name}
                if target_system.id not in systems:
                    systems[target_system.id] = {'id': target_system.id, 'name': target_system.name}
                
                edges.append({
                    'from': source_system.id,
                    'to': target_system.id,
                    'label': step.flow.service.name,
                    'step_order': step.step_order,
                    'protocol': step.flow.service.protocol,
                })
        
        context['steps'] = steps
        context['systems_json'] = json.dumps(list(systems.values()), ensure_ascii=False)
        context['edges_json'] = json.dumps(edges, ensure_ascii=False)
        
        return context

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
    model = IntegrationFlow
    template_name = 'repository/interaction_list.html'
    context_object_name = 'interactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        env_filter = self.request.GET.get('env', '')
        system_filter = self.request.GET.get('system', '')
        
        if search_query:
            queryset = queryset.filter(service__name__icontains=search_query)
        if env_filter:
            queryset = queryset.filter(environment=env_filter)
        if system_filter:
            queryset = queryset.filter(
                models.Q(source_system_id=system_filter) |
                models.Q(target_system_id=system_filter)
            )
        return queryset.select_related('service', 'source_system', 'target_system')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_env'] = self.request.GET.get('env', '')
        context['current_system'] = self.request.GET.get('system', '')
        context['systems'] = System.objects.all().order_by('name')
        return context


@method_decorator(login_required, name='dispatch')
class InteractionDetailView(DetailView):
    model = IntegrationFlow
    template_name = 'repository/interaction_detail.html'
    context_object_name = 'interaction'


@method_decorator(login_required, name='dispatch')
class InteractionCreateView(CreateView):
    model = IntegrationFlow
    form_class = IntegrationFlowForm
    template_name = 'repository/interaction_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграционный поток "{form.instance}" успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('interaction_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class InteractionUpdateView(UpdateView):
    model = IntegrationFlow
    form_class = IntegrationFlowForm
    template_name = 'repository/interaction_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграционный поток "{form.instance}" успешно обновлён!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('interaction_detail', kwargs={'pk': self.object.pk})


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
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля корректно')
    else:
        form = LoginForm()
    return render(request, 'repository/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('/accounts/login/')


# ==================== API VIEWS ====================

class DashboardAPIView(APIView):
    def get(self, request):
        return Response({
            'business_processes': BusinessProcess.objects.count(),
            'systems': System.objects.count(),
            'integrations': IntegrationFlow.objects.count(),
            'infrastructure': InfrastructureObject.objects.count(),
        })


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class BusinessProcessViewSet(viewsets.ModelViewSet):
    queryset = BusinessProcess.objects.all()
    serializer_class = BusinessProcessSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class IntegrationServiceViewSet(viewsets.ModelViewSet):
    queryset = IntegrationService.objects.all()
    serializer_class = IntegrationServiceSerializer


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


class InfrastructureObjectViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureObject.objects.all()
    serializer_class = InfrastructureObjectSerializer

class IntegrationFlowViewSet(viewsets.ModelViewSet):
    queryset = IntegrationFlow.objects.all()
    serializer_class = IntegrationFlowSerializer

@method_decorator(login_required, name='dispatch')
class IntegrationServiceListView(ListView):
    model = IntegrationService
    template_name = 'repository/service_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(login_required, name='dispatch')
class IntegrationServiceDetailView(DetailView):
    model = IntegrationService
    template_name = 'repository/service_detail.html'
    context_object_name = 'service'


@method_decorator(login_required, name='dispatch')
class IntegrationServiceCreateView(CreateView):
    model = IntegrationService
    form_class = IntegrationServiceForm
    template_name = 'repository/service_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграционный сервис "{form.instance.name}" успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('service_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class IntegrationServiceUpdateView(UpdateView):
    model = IntegrationService
    form_class = IntegrationServiceForm
    template_name = 'repository/service_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Интеграционный сервис "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('service_detail', kwargs={'pk': self.object.pk})