from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Complaint, ComplaintType, ComplaintStatus

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "client_number",
            "fix_phone_number",
            "phone_number",
            "address",
            "service_type",
            "user_type",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


    

class ComplaintSerializer(serializers.ModelSerializer):
    """
    Complaint CRUD.
    - `user` is read-only and taken from request.user
    - `reference_code` generated automatically
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Complaint
        fields = [
            "id",
            "user",
            "complaint_type",
            "description",
            "photo",
            "created_at",
            "updated_at",
            "status",
            "reference_code",
            "service_type",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "status",          # user cannot set status directly (only staff later)
            "reference_code",
        ]

   

