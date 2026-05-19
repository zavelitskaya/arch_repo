from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BusinessProcess, Scenario, ScenarioStep, IntegrationInteraction


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'example@mail.ru'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.'
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = '''
            <ul style="margin: 0; padding-left: 1rem; font-size: 0.75rem; color: #64748b;">
                <li>Пароль не должен быть слишком похож на вашу личную информацию</li>
                <li>Пароль должен содержать минимум 8 символов</li>
                <li>Пароль не может быть слишком простым или распространённым</li>
                <li>Пароль не может состоять только из цифр</li>
            </ul>
        '''
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = 'Введите тот же пароль, что и выше, для подтверждения.'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Имя пользователя', widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}), label='Пароль')


class BusinessProcessForm(forms.ModelForm):
    class Meta:
        model = BusinessProcess
        fields = ['code', 'name', 'description', 'business_owner']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: CRM-ORDER-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название процесса'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание процесса...'}),
            'business_owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО или должность бизнес-владельца'}),
        }
        labels = {
            'code': 'Код процесса',
            'name': 'Название',
            'description': 'Описание',
            'business_owner': 'Бизнес-владелец',
        }


class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', 'description', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название сценария'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание сценария...'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'checkbox-control'}),
        }
        labels = {
            'name': 'Название сценария',
            'description': 'Описание',
            'is_default': 'Основной сценарий',
        }


class ScenarioStepForm(forms.ModelForm):
    class Meta:
        model = ScenarioStep
        fields = ['step_order', 'step_type', 'interaction', 'condition_expression', 'true_next_step', 'false_next_step']
        widgets = {
            'step_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'step_type': forms.Select(attrs={'class': 'form-control', 'id': 'step-type'}),
            'interaction': forms.Select(attrs={'class': 'form-control', 'id': 'interaction-field'}),
            'condition_expression': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'например: сумма > 10000'}),
            'true_next_step': forms.Select(attrs={'class': 'form-control', 'id': 'true-next-field'}),
            'false_next_step': forms.Select(attrs={'class': 'form-control', 'id': 'false-next-field'}),
        }
        labels = {
            'step_order': 'Порядковый номер',
            'step_type': 'Тип шага',
            'interaction': 'Интеграционное взаимодействие',
            'condition_expression': 'Условие',
            'true_next_step': 'Переход при ИСТИНА',
            'false_next_step': 'Переход при ЛОЖЬ',
        }
    
    def __init__(self, *args, **kwargs):
        self.scenario = kwargs.pop('scenario', None)
        super().__init__(*args, **kwargs)
        
        if self.scenario:
            existing_steps = self.scenario.steps.all()
            self.fields['true_next_step'].queryset = existing_steps
            self.fields['false_next_step'].queryset = existing_steps
            self.fields['true_next_step'].required = False
            self.fields['false_next_step'].required = False
            
            systems = set()
            for step in existing_steps:
                if step.interaction:
                    systems.add(step.interaction.source_component.system)
                    systems.add(step.interaction.target_component.system)
            
            if systems:
                self.fields['interaction'].queryset = IntegrationInteraction.objects.filter(
                    source_component__system__in=systems
                ) | IntegrationInteraction.objects.filter(
                    target_component__system__in=systems
                )
            else:
                self.fields['interaction'].queryset = IntegrationInteraction.objects.all()


class IntegrationInteractionForm(forms.ModelForm):
    class Meta:
        model = IntegrationInteraction
        fields = ['name', 'service', 'source_component', 'target_component', 'protocol', 'method_type', 'method_detail', 'endpoint', 'environment', 'technical_description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: API вызов платежей'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'source_component': forms.Select(attrs={'class': 'form-control', 'id': 'source-component'}),
            'target_component': forms.Select(attrs={'class': 'form-control', 'id': 'target-component'}),
            'protocol': forms.Select(attrs={'class': 'form-control'}),
            'method_type': forms.Select(attrs={'class': 'form-control'}),
            'method_detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GET, POST, SUBSCRIBE...'}),
            'endpoint': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/api/v1/payments'}),
            'environment': forms.Select(attrs={'class': 'form-control'}),
            'technical_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Техническое описание...'}),
        }
        labels = {
            'name': 'Название интеграции',
            'service': 'Интеграционный сервис (бизнес-смысл)',
            'source_component': 'Компонент-источник',
            'target_component': 'Компонент-приёмник',
            'protocol': 'Протокол',
            'method_type': 'Тип метода',
            'method_detail': 'Детали метода',
            'endpoint': 'Endpoint',
            'environment': 'Среда',
            'technical_description': 'Техническое описание',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].required = False
        self.fields['method_detail'].required = False
        self.fields['endpoint'].required = False
        self.fields['technical_description'].required = False