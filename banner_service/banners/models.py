from django.db import models
import uuid

class Feature(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

class Banner(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.IntegerField(blank=True, null=True)
    feature_id = models.ForeignKey(Feature, on_delete=models.CASCADE, null=True, blank=True)
    tag_id = models.ManyToManyField(Tag, related_name='banners', blank=True)
    content = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    previous_version_uuid = models.UUIDField(null=True, blank=True)

