from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board

User = get_user_model()


class UserDataSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source="first_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return 0

    def get_tasks_to_do_count(self, obj):
        return 0

    def get_tasks_high_prio_count(self, obj):
        return 0


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        owner = self.context["request"].user

        board = Board.objects.create(owner=owner, **validated_data)
        board.members.set(members)

        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)

        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance
    

class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserDataSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        return []


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    owner_data = UserDataSerializer(source="owner", read_only=True)
    members_data = UserDataSerializer(source="members", many=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]