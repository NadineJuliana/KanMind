from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task
from .permissions import CanDeleteTask, IsTaskBoardMember
from .serializers import TaskCreateUpdateSerializer, TaskOutputSerializer


class AssignedToMeTaskListView(ListAPIView):
    serializer_class = TaskOutputSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskListView(ListAPIView):
    serializer_class = TaskOutputSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(CreateAPIView):
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        if not self._is_board_member(board_id, request.user):
            return Response(
                {"detail": "You must be a board member."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        data = TaskOutputSerializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    def _is_board_member(self, board_id, user):
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return board.owner == user or board.members.filter(id=user.id).exists()


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember, CanDeleteTask]
    lookup_url_kwarg = "task_id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskOutputSerializer
        return TaskCreateUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        data = TaskOutputSerializer(task).data
        return Response(data, status=status.HTTP_200_OK)