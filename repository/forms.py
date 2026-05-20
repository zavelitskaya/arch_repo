from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BusinessProcess, Scenario, ScenarioStep, IntegrationService, IntegrationFlow


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
        fields = ['step_order', 'flow', 'description']
        widgets = {
            'step_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'flow': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Описание шага...'}),
        }
        labels = {
            'step_order': 'Порядковый номер',
            'flow': 'Интеграционный поток',
            'description': 'Описание шага',
        }
    
    def __init__(self, *args, **kwargs):
        self.scenario = kwargs.pop('scenario', None)
        super().__init__(*args, **kwargs)
        self.fields['flow'].queryset = IntegrationFlow.objects.all()
        self.fields['flow'].required = False

        
class IntegrationServiceForm(forms.ModelForm):
    class Meta:
        model = IntegrationService
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'owner_system': forms.Select(attrs={'class': 'form-control'}),
            'protocol': forms.Select(attrs={'class': 'form-control', 'id': 'id_protocol'}),
            'pattern': forms.Select(attrs={'class': 'form-control', 'id': 'id_pattern'}),
            'endpoint': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'request_topic': forms.TextInput(attrs={'class': 'form-control'}),
            'response_topic': forms.TextInput(attrs={'class': 'form-control'}),
            'queue': forms.TextInput(attrs={'class': 'form-control'}),
            'request_queue': forms.TextInput(attrs={'class': 'form-control'}),
            'response_queue': forms.TextInput(attrs={'class': 'form-control'}),
            'exchange': forms.TextInput(attrs={'class': 'form-control'}),
            'routing_key': forms.TextInput(attrs={'class': 'form-control'}),
            'cluster': forms.TextInput(attrs={'class': 'form-control'}),
            'connection_string': forms.TextInput(attrs={'class': 'form-control'}),
            'query': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proto_service': forms.TextInput(attrs={'class': 'form-control'}),
            'proto_method': forms.TextInput(attrs={'class': 'form-control'}),
            'proto_schema_url': forms.URLInput(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_path': forms.TextInput(attrs={'class': 'form-control'}),
            'file_mask': forms.TextInput(attrs={'class': 'form-control'}),
            'request_schema': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'response_schema': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'message_schema': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'request_schema_url': forms.URLInput(attrs={'class': 'form-control'}),
            'response_schema_url': forms.URLInput(attrs={'class': 'form-control'}),
            'message_schema_url': forms.URLInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'is_deprecated': forms.CheckboxInput(attrs={'class': 'checkbox-control'}),
        }

class IntegrationFlowForm(forms.ModelForm):
    class Meta:
        model = IntegrationFlow
        fields = ['service', 'source_system', 'target_system', 'environment', 'status', 'description']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'source_system': forms.Select(attrs={'class': 'form-control'}),
            'target_system': forms.Select(attrs={'class': 'form-control'}),
            'environment': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Дополнительная информация...'}),
        }
        labels = {
            'service': 'Интеграционный сервис',
            'source_system': 'Система-поставщик',
            'target_system': 'Система-потребитель',
            'environment': 'Среда',
            'status': 'Статус',
            'description': 'Описание',
        }