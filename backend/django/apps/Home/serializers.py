from rest_framework import serializers

class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()

class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
