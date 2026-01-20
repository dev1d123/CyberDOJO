from django.contrib import admin
from django import forms
from .models import CyberUser, Country, RiskLevel, Preferences


class CyberUserAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Introduce la contraseña en texto plano. Se hasheará automáticamente."
    )
    
    class Meta:
        model = CyberUser
        fields = '__all__'


@admin.register(CyberUser)
class CyberUserAdmin(admin.ModelAdmin):
    form = CyberUserAdminForm
    list_display = ['username', 'email', 'is_active', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['is_active', 'country', 'risk_level']
    
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            # Si se está editando y la contraseña cambió, hashearla
            if change:
                old_obj = CyberUser.objects.get(pk=obj.pk)
                if old_obj.password != form.cleaned_data['password']:
                    obj.set_password(form.cleaned_data['password'])
            else:
                # Si es un nuevo usuario, hashear la contraseña
                obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


admin.site.register(Country)
admin.site.register(RiskLevel)
admin.site.register(Preferences)
