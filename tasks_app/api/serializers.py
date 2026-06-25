from rest_framework import serializers
from auth_app.api.serializers import UserDataSerializer

from tasks_app.models import Task, Comment


class TaskOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for task response data.
    """

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
        """
        Returns the number of comments assigned to the task.
        """

        return obj.comments.count()


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating and updating tasks.
    """

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
        """
        Validates that the selected assignee and reviewer belong
        to the associated board.
        """

        board = self._get_board(attrs)
        self._validate_board_member(board, attrs.get("assignee_id"))
        self._validate_board_member(board, attrs.get("reviewer_id"))
        return attrs

    def create(self, validated_data):
        """
        Creates a new task, assigns the authenticated user as creator,
        and sets the assignee and reviewer.
        """

        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)
        user = self.context["request"].user
        task = Task.objects.create(created_by=user, **validated_data)
        self._set_users(task, assignee_id, reviewer_id)
        return task

    def update(self, instance, validated_data):
        """
        Updates a task and its assigned users.
        """

        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        self._set_users(instance, assignee_id, reviewer_id)
        return instance

    def _get_board(self, attrs):
        """
        Returns the associated board for validation during
        task creation or update.
        """

        if self.instance:
            return self.instance.board
        return attrs.get("board")

    def _validate_board_member(self, board, user_id):
        """
        Ensures that assignee and reviewer belong to the selected board.
        """

        if user_id is None:
            return

        is_member = board.members.filter(id=user_id).exists()
        is_owner = board.owner_id == user_id

        if not is_member and not is_owner:
            raise serializers.ValidationError(
                "Assignee and reviewer must be board members."
            )

    def _set_users(self, task, assignee_id, reviewer_id):
        """
        Assigns the assignee and reviewer to the task and saves it.
        """

        task.assignee_id = assignee_id
        task.reviewer_id = reviewer_id
        task.save()


class BoardTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task data included in board detail responses.
    """

    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
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
        """
        Returns the number of comments assigned to the task.
        """

        return obj.comments.count()


class CommentOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for comment response data.
    """

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
    """
    Serializer used for creating comments.
    """

    class Meta:
        model = Comment
        fields = ["content"]
