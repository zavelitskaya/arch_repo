from django.contrib import admin
from .models import (
    Team, BusinessProcess, Scenario, ScenarioStep,
    IntegrationService, IntegrationInteraction,
    System, Component, InfrastructureObject, ComponentInfrastructureLink
)


class ScenarioStepInline(admin.TabularInline):
    model = ScenarioStep
    extra = 1
    fields = ['step_order', 'step_type', 'interaction', 'condition_expression', 'true_next_step', 'false_next_step']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'slack_channel', 'email')
    search_fields = ('name',)


@admin.register(BusinessProcess)
class BusinessProcessAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'business_owner', 'created_at')
    list_filter = ('business_owner',)
    search_fields = ('code', 'name')
    inlines = []


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_process', 'is_default')
    list_filter = ('business_process', 'is_default')
    search_fields = ('name',)
    inlines = [ScenarioStepInline]


@admin.register(ScenarioStep)
class ScenarioStepAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'step_order', 'step_type', 'interaction')
    list_filter = ('step_type', 'scenario__business_process')
    search_fields = ('condition_expression',)


@admin.register(IntegrationService)
class IntegrationServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_owner', 'data_contract_version', 'created_at')
    list_filter = ('data_owner',)
    search_fields = ('name', 'business_purpose')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_team')
    list_filter = ('owner_team',)
    search_fields = ('name',)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'component_type', 'technical_owner')
    list_filter = ('system', 'component_type')
    search_fields = ('name',)


@admin.register(InfrastructureObject)
class InfrastructureObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_type', 'technology')
    list_filter = ('object_type', 'technology')
    search_fields = ('name',)


@admin.register(ComponentInfrastructureLink)
class ComponentInfrastructureLinkAdmin(admin.ModelAdmin):
    list_display = ('component', 'infrastructure_object', 'role')
    list_filter = ('role',)
    search_fields = ('component__name', 'infrastructure_object__name')


@admin.register(IntegrationInteraction)
class IntegrationInteractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'source_component', 'target_component', 'protocol', 'environment')
    list_filter = ('protocol', 'method_type', 'environment', 'service')
    search_fields = ('name', 'endpoint')