from rest_framework import serializers
from .models import (
    Team, BusinessProcess, Scenario, ScenarioStep,
    IntegrationService, IntegrationInteraction,
    System, Component, InfrastructureObject, ComponentInfrastructureLink
)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class ComponentSerializer(serializers.ModelSerializer):
    system_name = serializers.CharField(source='system.name', read_only=True)
    
    class Meta:
        model = Component
        fields = ['id', 'name', 'system', 'system_name', 'component_type', 'technical_owner', 'description']


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


class IntegrationInteractionSerializer(serializers.ModelSerializer):
    source_component_name = serializers.CharField(source='source_component.name', read_only=True)
    target_component_name = serializers.CharField(source='target_component.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = IntegrationInteraction
        fields = '__all__'


class IntegrationServiceSerializer(serializers.ModelSerializer):
    interactions = IntegrationInteractionSerializer(many=True, read_only=True)
    
    class Meta:
        model = IntegrationService
        fields = ['id', 'name', 'business_purpose', 'data_owner', 'data_contract_version', 'interactions', 'created_at']


class ScenarioStepSerializer(serializers.ModelSerializer):
    interaction_detail = IntegrationInteractionSerializer(source='interaction', read_only=True)
    
    class Meta:
        model = ScenarioStep
        fields = ['id', 'step_order', 'step_type', 'condition_expression', 'interaction', 'interaction_detail', 
                  'true_next_step', 'false_next_step']


class ScenarioSerializer(serializers.ModelSerializer):
    steps = ScenarioStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Scenario
        fields = ['id', 'name', 'description', 'is_default', 'steps']


class BusinessProcessSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True, read_only=True)
    business_owner_name = serializers.CharField(source='business_owner.name', read_only=True, allow_null=True)
    
    class Meta:
        model = BusinessProcess
        fields = ['id', 'code', 'name', 'description', 'business_owner', 'business_owner_name', 
                  'scenarios', 'created_at', 'updated_at']


class SystemSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = System
        fields = ['id', 'name', 'description', 'owner_team', 'components']