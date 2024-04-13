from rest_framework import serializers
from .models import Feature, Tag, Banner

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    tag_ids = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Banner
        fields = '__all__'
