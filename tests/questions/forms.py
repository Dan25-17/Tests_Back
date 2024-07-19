from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser