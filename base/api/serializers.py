from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from base.models import User, Location, Work, Notice, Notification, Feedback, Report



# Unified User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid", "email", "name", "password", "role", "designation", "organization",
            "national_id", "phone_number", "city", "created_at", "updated_at", "is_active"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["authority", "stakeholder", "citizen"])
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        try:
            user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email, role, or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email, role, or password")

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["uuid", "city", "geom"]



class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = [
            "uuid", "stakeholder", "location", "name", "details", "tag", "status",
            "estimated_time", "proposed_start_date", "proposed_end_date",
            "start_date", "end_date", "budget", "conflicts",
            "created_at", "updated_at"
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) == 'stakeholder':
                stakeholder_uuid = str(validated_data.get('stakeholder').uuid)
                user_uuid = str(request.user.uuid)
                if stakeholder_uuid != user_uuid:
                    raise serializers.ValidationError("Stakeholder field must match your user UUID.")
        return super().create(validated_data)


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "uuid", "ordinance_no", "name", "details", "created_at", "updated_at", "created_by", "attached_file"
        ]
        extra_kwargs = {
            "attached_file": {"required": False},
            "created_by": {"required": False},
        }

    def validate_attached_file(self, value):
        if value and not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'authority':
                raise serializers.ValidationError("Only authority users can create notices.")
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'authority':
                raise serializers.ValidationError("Only authority users can update notices.")
        return super().update(instance, validated_data)

    def delete(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'authority':
                raise serializers.ValidationError("Only authority users can delete notices.")
        return super().delete(instance)
    

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "uuid", "genre", "details", "is_read", "created_at", "updated_at", "created_by", "created_for", "related_work"
        ]
        extra_kwargs = {
            "related_work": {"required": False},
            "created_by": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'authority':
                raise serializers.ValidationError("Only authority users can create notifications.")
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'authority':
                raise serializers.ValidationError("Only authority users can update notifications.")
        return super().update(instance, validated_data)
    

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "uuid", "created_by", "details", "feeling", "related_work", "created_at", "updated_at"
        ]
        extra_kwargs = {
            "related_work": {"required": False},
            "created_by": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'citizen':
                raise serializers.ValidationError("Only citizen users can create feedback.")
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if getattr(request.user, 'role', None) != 'citizen':
                raise serializers.ValidationError("Only citizen users can update feedback.")
        return super().update(instance, validated_data)
    

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "uuid", "report_type", "status", "details", "created_by", "related_work", "created_at", "updated_at"
        ]
        extra_kwargs = {
            "related_work": {"required": False},
            "created_by": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if instance.created_by != request.user:
                raise serializers.ValidationError("You can only update your own reports.")
        return super().update(instance, validated_data)