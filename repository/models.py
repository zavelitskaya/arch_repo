from django.db import models
from django.core.exceptions import ValidationError


class Team(models.Model):
    """Команда (владелец процессов и данных)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название команды")
    slack_channel = models.CharField(max_length=100, blank=True, verbose_name="Slack канал")
    email = models.EmailField(blank=True, verbose_name="Email")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"


class Tag(models.Model):
    """Теги для классификации"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="Цвет (HEX)")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


# ==================== УРОВЕНЬ 1: БИЗНЕС-ПРОЦЕССЫ ====================

class BusinessProcess(models.Model):
    """Бизнес-процесс"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Код процесса")
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    business_owner = models.CharField(max_length=200, blank=True, verbose_name="Бизнес-владелец")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"[{self.code}] {self.name}"

    class Meta:
        verbose_name = "Бизнес-процесс"
        verbose_name_plural = "Бизнес-процессы"


class ProcessDocument(models.Model):
    """Документы, прикреплённые к бизнес-процессу"""
    business_process = models.ForeignKey(BusinessProcess, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='process_documents/%Y/%m/%d/', verbose_name="Файл")
    description = models.CharField(max_length=200, blank=True, verbose_name="Описание")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    uploaded_by = models.CharField(max_length=100, blank=True, verbose_name="Кто загрузил")

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Документ процесса"
        verbose_name_plural = "Документы процессов"


class Scenario(models.Model):
    """Сценарий бизнес-процесса"""
    name = models.CharField(max_length=200, verbose_name="Название сценария")
    description = models.TextField(blank=True, verbose_name="Описание")
    business_process = models.ForeignKey(BusinessProcess, on_delete=models.CASCADE, related_name='scenarios')
    is_default = models.BooleanField(default=False, verbose_name="Основной сценарий")

    def __str__(self):
        return f"{self.business_process.name} → {self.name}"

    class Meta:
        verbose_name = "Сценарий"
        verbose_name_plural = "Сценарии"


class ScenarioStep(models.Model):
    """Шаг сценария (с поддержкой ветвлений)"""
    STEP_TYPES = [
        ('ordinary', 'Обычный шаг'),
        ('condition', 'Ветвление'),
    ]

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='steps')
    step_order = models.PositiveIntegerField(verbose_name="Порядок шага")
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, default='ordinary')
    
    condition_expression = models.TextField(blank=True, verbose_name="Условие")
    true_next_step = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='true_branch')
    false_next_step = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='false_branch')
    flow = models.ForeignKey('IntegrationFlow', on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='steps', verbose_name="Интеграционный поток")

    def clean(self):
        if self.step_type == 'condition':
            if not self.condition_expression:
                raise ValidationError({'condition_expression': 'Для ветвления нужно указать условие'})
            if not self.true_next_step or not self.false_next_step:
                raise ValidationError('Для ветвления нужно указать оба перехода')
            for next_step in [self.true_next_step, self.false_next_step]:
                if next_step and next_step.scenario != self.scenario:
                    raise ValidationError('Переходы должны быть в рамках того же сценария')
        else:
            if not self.flow:
                raise ValidationError({'flow': 'Для обычного шага нужно указать интеграционный поток'})

    def __str__(self):
        return f"Шаг {self.step_order}: {self.get_step_type_display()}"

    class Meta:
        verbose_name = "Шаг сценария"
        verbose_name_plural = "Шаги сценария"
        ordering = ['scenario', 'step_order']
        unique_together = ['scenario', 'step_order']


# ==================== УРОВЕНЬ 2: ИНТЕГРАЦИОННЫЕ СЕРВИСЫ И ПОТОКИ ====================

class IntegrationService(models.Model):
    class Protocol(models.TextChoices):
        HTTP = 'http', 'HTTP'
        KAFKA = 'kafka', 'Kafka'
        MQ = 'mq', 'Message Queue'
        JDBC = 'jdbc', 'JDBC'
        GRPC = 'grpc', 'gRPC'
        SFTP = 'sftp', 'SFTP'
    
    class Pattern(models.TextChoices):
        REQUEST_RESPONSE = 'reqresp', 'Запрос-ответ'
        EVENT = 'event', 'Событие (broadcast)'
        DATABASE = 'db', 'Запрос к БД'
        FILE = 'file', 'Файловый обмен'
    
    name = models.CharField(max_length=200, unique=True, verbose_name="Название сервиса")
    business_purpose = models.TextField(verbose_name="Бизнес-смысл")
    owner_system = models.ForeignKey('System', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Владелец сервиса")
    
    protocol = models.CharField(max_length=20, choices=Protocol.choices, verbose_name="Протокол")
    pattern = models.CharField(max_length=20, choices=Pattern.choices, verbose_name="Паттерн")
    
    # Общие для запрос-ответ
    request_schema = models.JSONField(null=True, blank=True, verbose_name="Схема запроса")
    response_schema = models.JSONField(null=True, blank=True, verbose_name="Схема ответа")
    request_schema_url = models.URLField(blank=True, verbose_name="Ссылка на схему запроса")
    response_schema_url = models.URLField(blank=True, verbose_name="Ссылка на схему ответа")
    
    # Общие для события
    message_schema = models.JSONField(null=True, blank=True, verbose_name="Схема сообщения")
    message_schema_url = models.URLField(blank=True, verbose_name="Ссылка на схему сообщения")
    
    # HTTP
    endpoint = models.CharField(max_length=500, blank=True, verbose_name="Endpoint")
    
    # Kafka / MQ
    topic = models.CharField(max_length=200, blank=True, verbose_name="Топик")
    request_topic = models.CharField(max_length=200, blank=True, verbose_name="Request topic")
    response_topic = models.CharField(max_length=200, blank=True, verbose_name="Response topic")
    queue = models.CharField(max_length=200, blank=True, verbose_name="Очередь")
    request_queue = models.CharField(max_length=200, blank=True, verbose_name="Request queue")
    response_queue = models.CharField(max_length=200, blank=True, verbose_name="Response queue")
    exchange = models.CharField(max_length=200, blank=True, verbose_name="Exchange")
    routing_key = models.CharField(max_length=200, blank=True, verbose_name="Routing key")
    cluster = models.CharField(max_length=200, blank=True, verbose_name="Кластер")
    
    # JDBC
    connection_string = models.CharField(max_length=500, blank=True, verbose_name="Connection string")
    query = models.TextField(blank=True, verbose_name="SQL запрос")
    
    # gRPC
    proto_service = models.CharField(max_length=200, blank=True, verbose_name="Proto service")
    proto_method = models.CharField(max_length=200, blank=True, verbose_name="Proto method")
    proto_schema_url = models.URLField(blank=True, verbose_name="Proto schema URL")
    
    # SFTP
    host = models.CharField(max_length=200, blank=True, verbose_name="Хост")
    port = models.IntegerField(default=22, blank=True, verbose_name="Порт")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Путь к файлу")
    file_mask = models.CharField(max_length=100, blank=True, verbose_name="Маска файла")
    
    # Версионирование
    version = models.CharField(max_length=20, default='1.0.0', verbose_name="Версия")
    is_deprecated = models.BooleanField(default=False, verbose_name="Устаревший")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

    class Meta:
        verbose_name = "Интеграционный сервис"
        verbose_name_plural = "Интеграционные сервисы"
class IntegrationFlow(models.Model):
    """Интеграционный поток (использование сервиса конкретными системами)"""
    
    class Environment(models.TextChoices):
        DEV = 'dev', 'Разработка'
        STAGE = 'stage', 'Стейджинг'
        PROD = 'prod', 'Продакшн'
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        TESTING = 'testing', 'Тестируется'
        PLANNED = 'planned', 'Планируется'
        DEPRECATED = 'deprecated', 'Устаревший'
    
    service = models.ForeignKey(IntegrationService, on_delete=models.CASCADE, related_name='flows', verbose_name="Интеграционный сервис")
    
    source_system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='source_flows', verbose_name="Система-поставщик (источник)")
    target_system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='target_flows', verbose_name="Система-потребитель")
    
    environment = models.CharField(max_length=10, choices=Environment.choices, default=Environment.PROD, verbose_name="Среда")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name="Статус")
    
    description = models.TextField(blank=True, verbose_name="Примечание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source_system.name} → {self.target_system.name}: {self.service.name} [{self.get_environment_display()}]"

    class Meta:
        verbose_name = "Интеграционный поток"
        verbose_name_plural = "Интеграционные потоки"
        unique_together = ['service', 'source_system', 'target_system', 'environment']


# ==================== УРОВЕНЬ 3: СИСТЕМЫ, КОМПОНЕНТЫ, ИНФРАСТРУКТУРА ====================

class System(models.Model):
    """Система (контейнер)"""
    class Criticality(models.IntegerChoices):
        LOW = 1, 'Низкая'
        MEDIUM = 2, 'Средняя'
        HIGH = 3, 'Высокая'
        CRITICAL = 4, 'Критическая'
    
    class Lifecycle(models.TextChoices):
        PLANNED = 'planned', 'Планируется'
        DEVELOPMENT = 'development', 'В разработке'
        PRODUCTION = 'production', 'В продуктивной эксплуатации'
        DEPRECATED = 'deprecated', 'Устаревшая'
        DECOMMISSIONED = 'decommissioned', 'Выведена из эксплуатации'
    
    name = models.CharField(max_length=200, verbose_name="Название системы")
    description = models.TextField(blank=True, verbose_name="Описание")
    owner_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, verbose_name="Команда-владелец")
    
    criticality = models.IntegerField(choices=Criticality.choices, default=Criticality.MEDIUM, verbose_name="Критичность")
    lifecycle_stage = models.CharField(max_length=20, choices=Lifecycle.choices, default=Lifecycle.DEVELOPMENT, verbose_name="Стадия")
    sla_required = models.CharField(max_length=50, blank=True, verbose_name="Требуемый SLA")
    documentation_url = models.URLField(blank=True, verbose_name="Документация")
    repository_url = models.URLField(blank=True, verbose_name="Репозиторий")
    compliance_requirements = models.TextField(blank=True, verbose_name="Комплаенс")
    tags = models.ManyToManyField(Tag, blank=True, related_name='systems', verbose_name="Теги")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Система"
        verbose_name_plural = "Системы"


class Component(models.Model):
    """Компонент (микросервис, модуль, приложение)"""
    COMPONENT_TYPES = [
        ('microservice', 'Микросервис'),
        ('module', 'Модуль'),
        ('batch', 'Батч'),
        ('legacy', 'Legacy-приложение'),
    ]
    
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=200)
    component_type = models.CharField(max_length=30, choices=COMPONENT_TYPES)
    technical_owner = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.system.name} → {self.name}"

    class Meta:
        verbose_name = "Компонент"
        verbose_name_plural = "Компоненты"


class InfrastructureObject(models.Model):
    """Инфраструктурный объект (БД, очередь, кэш, хранилище)"""
    OBJECT_TYPES = [
        ('database', 'База данных'),
        ('message_queue', 'Очередь сообщений'),
        ('cache', 'Кэш'),
        ('storage', 'Хранилище'),
        ('kafka', 'Kafka'),
    ]
    
    name = models.CharField(max_length=200)
    object_type = models.CharField(max_length=30, choices=OBJECT_TYPES)
    technology = models.CharField(max_length=50)
    version = models.CharField(max_length=20, blank=True, verbose_name="Версия")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.technology})"

    class Meta:
        verbose_name = "Инфраструктурный объект"
        verbose_name_plural = "Инфраструктурные объекты"


class ComponentInfrastructureLink(models.Model):
    """Связь компонента с инфраструктурой (с ролью)"""
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='infra_links')
    infrastructure_object = models.ForeignKey(InfrastructureObject, on_delete=models.CASCADE, related_name='component_links')
    role = models.CharField(max_length=50, blank=True, verbose_name="Роль")

    def __str__(self):
        return f"{self.component.name} → {self.infrastructure_object.name} [{self.role}]"

    class Meta:
        verbose_name = "Связь компонента с инфраструктурой"
        verbose_name_plural = "Связи компонентов с инфраструктурой"
        unique_together = ['component', 'infrastructure_object', 'role']