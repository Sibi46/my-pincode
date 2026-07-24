from django import forms
from .models import Business, BusinessCategory


class BusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'business_name', 'owner_name', 'category',
            'mobile', 'email', 'website', 'description',
            'address', 'pincode', 'city', 'state',
            'gst_number', 'pan_number',
            'logo', 'cover_image',
            'facebook', 'instagram', 'twitter',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'placeholder': 'e.g. Sibi\'s Kitchen'}),
            'owner_name':    forms.TextInput(attrs={'placeholder': 'Full name of business owner'}),
            'mobile':        forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'email':         forms.EmailInput(attrs={'placeholder': 'business@email.com'}),
            'website':       forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com (optional)'}),
            'address':       forms.Textarea(attrs={'rows': 3, 'placeholder': 'Full business address'}),
            'pincode':       forms.TextInput(attrs={'placeholder': '6-digit pincode', 'maxlength': '10'}),
            'city':          forms.TextInput(attrs={'placeholder': 'City'}),
            'state':         forms.TextInput(attrs={'placeholder': 'State'}),
            'gst_number':    forms.TextInput(attrs={'placeholder': 'GST number (optional)'}),
            'pan_number':    forms.TextInput(attrs={'placeholder': 'PAN number (optional)'}),
            'description':   forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description of your business'}),
            'facebook':      forms.URLInput(attrs={'placeholder': 'Facebook page URL (optional)'}),
            'instagram':     forms.URLInput(attrs={'placeholder': 'Instagram profile URL (optional)'}),
            'twitter':       forms.URLInput(attrs={'placeholder': 'Twitter/X profile URL (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = BusinessCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = '— Select Category —'
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput,
                                         forms.URLInput, forms.Textarea, forms.Select)):
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()
