from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists')
        return value

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email') or ''
        password = validated_data.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
