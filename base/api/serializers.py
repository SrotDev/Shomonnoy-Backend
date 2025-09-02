from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from base.models import Authority, Stakeholder, Citizen


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = [
            "uuid", "email", "name", "password", "designation", "organization",
            "phone_number", "city", "created_at", "updated_at", "is_active"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Authority(**validated_data)
        user.set_password(password)
        user.save()
        return user


class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = [
            "uuid", "email", "name", "password", "designation", "organization",
            "phone_number", "city", "created_at", "updated_at", "is_active"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Stakeholder(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = [
            "uuid", "email", "name", "password", "national_id", "phone_number", "city", "created_at", "updated_at", "is_active"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Citizen(**validated_data)
        user.set_password(password)
        user.save()
        return user


# -------- Authentication Serializer ----------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=["authority", "stakeholder", "citizen"])
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user_type = data.get("user_type")

        model_map = {
            "authority": Authority,
            "stakeholder": Stakeholder,
            "citizen": Citizen,
        }
        model = model_map[user_type]

        try:
            user = model.objects.get(email=email)
        except model.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
