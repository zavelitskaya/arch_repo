from rest_framework import serializers
from .models import (
    Team, BusinessProcess, Scenario, ScenarioStep,
    IntegrationService, IntegrationFlow,
    System, Component, InfrastructureObject, ComponentInfrastructureLink
)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class BusinessProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProcess
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = '__all__'


class ScenarioStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioStep
        fields = '__all__'


class IntegrationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationService
        fields = '__all__'


class IntegrationFlowSerializer(serializers.ModelSerializer):
    source_system_name = serializers.CharField(source='source_system.name', read_only=True)
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = IntegrationFlow
        fields = '__all__'


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = '__all__'


class ComponentSerializer(serializers.ModelSerializer):
    system_name = serializers.CharField(source='system.name', read_only=True)
    
    class Meta:
        model = Component
        fields = ['id', 'name', 'system', 'system_name', 'component_type', 'technical_owner', 'description', 'created_at', 'updated_at']


class InfrastructureObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureObject
        fields = '__all__'


class ComponentInfrastructureLinkSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='component.name', read_only=True)
    infrastructure_object_name = serializers.CharField(source='infrastructure_object.name', read_only=True)
    
    class Meta:
        model = ComponentInfrastructureLink
        fields = ['id', 'component', 'component_name', 'infrastructure_object', 'infrastructure_object_name', 'role']