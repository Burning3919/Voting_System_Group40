from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Customer, Poll, Option, Administrator


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'email', 'password']
        read_only_fields = ['customer_id']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'email']
        read_only_fields = ['customer_id']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option_id', 'content', 'count']


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ['poll_id', 'title', 'created_at', 'cut_off', 'active', 'options']


class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = ['admin_id']
        extra_kwargs = {'admin_psw': {'write_only': True}}


