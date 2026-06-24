from rest_framework import serializers
from boards_app.api.serializers import UserDataSerializer
from tasks_app.models import Task, Comment


class TaskOutputSerializer(serializers.ModelSerializer):
    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return 0


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate(self, attrs):
        board = self._get_board(attrs)
        self._validate_board_member(board, attrs.get("assignee_id"))
        self._validate_board_member(board, attrs.get("reviewer_id"))
        return attrs

    def create(self, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)
        user = self.context["request"].user

        task = Task.objects.create(created_by=user, **validated_data)
        self._set_users(task, assignee_id, reviewer_id)
        return task

    def update(self, instance, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        self._set_users(instance, assignee_id, reviewer_id)
        return instance

    def _get_board(self, attrs):
        if self.instance:
            return self.instance.board
        return attrs.get("board")

    def _validate_board_member(self, board, user_id):
        if user_id is None:
            return

        is_member = board.members.filter(id=user_id).exists()
        is_owner = board.owner_id == user_id

        if not is_member and not is_owner:
            raise serializers.ValidationError(
                "Assignee and reviewer must be board members."
            )

    def _set_users(self, task, assignee_id, reviewer_id):
        task.assignee_id = assignee_id
        task.reviewer_id = reviewer_id
        task.save()


class CommentOutputSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source="author.first_name",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]