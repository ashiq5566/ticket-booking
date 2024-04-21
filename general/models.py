import os
import uuid
from django.db import models


def generate_image_path(instance, filename, image_category):
    """
    Generate the file path for storing images based on the image category.

    Args:
        instance: The instance of the model.
        filename (str): The original filename of the uploaded image.
        image_category (str): The category or type of the image (e.g., 'islamic-post-tag', 'islamic-post').

    Returns:
        str: The file path where the image should be stored.
    """
    upload_path = f"accounts/media/{image_category}-image"
    return os.path.join(upload_path, filename)

def get_country_flag_image_path(instance, filename):
    return generate_image_path(instance, filename, 'country-flag')



class WebBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auto_id = models.PositiveIntegerField(db_index=True,unique=True)
    date_added = models.DateTimeField(db_index=True,auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auto_id = models.PositiveIntegerField(db_index=True,unique=True)
    creator = models.ForeignKey("accounts.User", related_name="creator_%(class)s_objects", on_delete=models.CASCADE, null=True, blank=True)
    updater = models.ForeignKey("accounts.User", related_name="updater_%(class)s_objects", on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(db_index=True,auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        
    
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, null=True, blank=True)
    web_code = models.CharField(max_length=128, null=True, blank=True)
    country_code = models.CharField(max_length=128, null=True)
    phone_code = models.CharField(max_length=128, null=True, blank=True)
    phone_number_length = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    flag = models.ImageField(upload_to=get_country_flag_image_path, blank=True, null=True)
    order_id = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = 'general_country'
        verbose_name = ('country')
        verbose_name_plural = ('countries')
        ordering = ('name',)

    def __str__(self):
        return self.name
        