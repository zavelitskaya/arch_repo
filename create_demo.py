import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from repository.models import *

print("🔧 Создаём демо-данные...")

# 1. Команды
backend = Team.objects.create(name="Backend Team", slack_channel="#backend")
frontend = Team.objects.create(name="Frontend Team", slack_channel="#frontend")
devops = Team.objects.create(name="DevOps Team", slack_channel="#devops")

# 2. Бизнес-процесс
process = BusinessProcess.objects.create(
    code="ORDER-001",
    name="Обработка заказа",
    description="Процесс оформления и оплаты заказа в интернет-магазине",
    business_owner=backend
)

# 3. Сценарий
scenario = Scenario.objects.create(
    name="Успешная оплата картой",
    description="Клиент добавляет товары, оформляет заказ, успешно оплачивает картой",
    business_process=process,
    is_default=True
)

# 4. Системы и компоненты
crm_system = System.objects.create(name="CRM система", owner_team=backend)
payment_system = System.objects.create(name="Платёжный шлюз", owner_team=backend)
notify_system = System.objects.create(name="Система уведомлений", owner_team=frontend)

crm_component = Component.objects.create(
    system=crm_system,
    name="order-service",
    component_type="microservice",
    technical_owner="Иван Иванов"
)

payment_component = Component.objects.create(
    system=payment_system,
    name="payment-gateway",
    component_type="microservice",
    technical_owner="Пётр Петров"
)

notify_component = Component.objects.create(
    system=notify_system,
    name="notify-sender",
    component_type="microservice",
    technical_owner="Мария Смирнова"
)

# 5. Инфраструктура
order_db = InfrastructureObject.objects.create(
    name="Заказы PostgreSQL",
    object_type="database",
    technology="PostgreSQL 15"
)

redis_cache = InfrastructureObject.objects.create(
    name="Кэш Redis",
    object_type="cache",
    technology="Redis 7"
)

# Связи компонентов с инфраструктурой
ComponentInfrastructureLink.objects.create(
    component=crm_component,
    infrastructure_object=order_db,
    role="primary_db"
)
ComponentInfrastructureLink.objects.create(
    component=crm_component,
    infrastructure_object=redis_cache,
    role="cache_layer"
)

# 6. Интеграционный сервис (бизнес-смысл)
integration_service = IntegrationService.objects.create(
    name="Передача данных заказа на оплату",
    business_purpose="Передать сумму заказа, номер карты и вернуть статус оплаты",
    data_owner=backend,
    data_contract_version="1.0.0"
)

# 7. Интеграционное взаимодействие (техническая реализация)
interaction = IntegrationInteraction.objects.create(
    name="order-service → payment-gateway",
    service=integration_service,
    source_component=crm_component,
    target_component=payment_component,
    protocol="https",
    method_type="sync_call",
    method_detail="POST",
    endpoint="/api/v1/payments",
    environment="prod",
    technical_description="Передаём данные заказа в платёжный шлюз"
)

# 8. Связываем шаг сценария с взаимодействием
step = ScenarioStep.objects.create(
    scenario=scenario,
    step_order=1,
    step_type="ordinary",
    interaction=interaction,
    condition_expression=""
)

print("✅ Демо-данные созданы!")
print(f"   Бизнес-процесс: {process.name}")
print(f"   Сценарий: {scenario.name}")
print(f"   Компонентов: {Component.objects.count()}")
print(f"   Взаимодействий: {IntegrationInteraction.objects.count()}")