from django.contrib import admin
from .models import (
    Team, Tag, BusinessProcess, ProcessDocument, Scenario, ScenarioStep,
    IntegrationService, IntegrationFlow,
    System, Component, InfrastructureObject, ComponentInfrastructureLink
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'slack_channel', 'email')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(BusinessProcess)
class BusinessProcessAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'business_owner', 'created_at')
    list_filter = ('business_owner',)
    search_fields = ('code', 'name')


@admin.register(ProcessDocument)
class ProcessDocumentAdmin(admin.ModelAdmin):
    list_display = ('business_process', 'file', 'uploaded_at', 'uploaded_by')
    list_filter = ('business_process',)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_process', 'is_default')
    list_filter = ('business_process', 'is_default')
    search_fields = ('name',)


@admin.register(ScenarioStep)
class ScenarioStepAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'step_order', 'step_type', 'flow')
    list_filter = ('step_type', 'scenario__business_process')
    search_fields = ('condition_expression',)


@admin.register(IntegrationService)
class IntegrationServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'protocol', 'owner_system', 'is_deprecated')
    list_filter = ('protocol', 'is_deprecated', 'owner_system')
    search_fields = ('name', 'business_purpose')


@admin.register(IntegrationFlow)
class IntegrationFlowAdmin(admin.ModelAdmin):
    list_display = ('service', 'source_system', 'target_system', 'environment', 'status')
    list_filter = ('environment', 'status', 'service')
    search_fields = ('service__name', 'source_system__name', 'target_system__name')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_team', 'criticality', 'lifecycle_stage')
    list_filter = ('owner_team', 'criticality', 'lifecycle_stage')
    search_fields = ('name',)
    filter_horizontal = ('tags',)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'component_type', 'technical_owner')
    list_filter = ('system', 'component_type')
    search_fields = ('name',)


@admin.register(InfrastructureObject)
class InfrastructureObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_type', 'technology', 'version')
    list_filter = ('object_type', 'technology')
    search_fields = ('name',)


@admin.register(ComponentInfrastructureLink)
class ComponentInfrastructureLinkAdmin(admin.ModelAdmin):
    list_display = ('component', 'infrastructure_object', 'role')
    list_filter = ('role',)
    search_fields = ('component__name', 'infrastructure_object__name')