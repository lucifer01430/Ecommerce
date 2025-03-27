from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile', null=True, blank=True)


@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())  # ✅ Pehle token generate karo
            profile, created = Profile.objects.get_or_create(user=instance)
            
            if created:  # ✅ Duplicate Profile avoid karne ke liye
                profile.email_token = email_token
                profile.save()

                send_account_activation_email(instance.email, email_token)
    
    except Exception as e:
        print("Error:", e)
        return False
