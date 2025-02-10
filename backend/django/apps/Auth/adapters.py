from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new user instance using information provided in the form.
        """
        data = form.cleaned_data
        user.username = data.get('username')
        user.email = data.get('email')
        
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
            
        self.populate_username(request, user)
        
        if commit:
            user.save()
        return user

    def clean_password(self, password, user=None):
        """
        Temporary removal of password validation
        """
        return password

    def populate_username(self, request, user):
        """
        Sets the username if it's not provided.
        """
        username = user.username
        if not username:
            username = user.email.split('@')[0]
            user.username = username
