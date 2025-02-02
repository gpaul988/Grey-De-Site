from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Foreign key to link to users using a string reference
    admin = models.ForeignKey('authentication.User', related_name='company_admins', on_delete=models.CASCADE)

    def __str__(self):
        return self.name