from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board

from .permissions import IsBoardOwnerForDelete, IsBoardOwnerOrMember
from .serializers import (
    BoardCreateUpdateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateResponseSerializer,
    UserDataSerializer,
)

User = get_user_model()


class BoardListCreateView(ListCreateAPIView):
    """
    Handles listing and creating boards for the authenticated user.
    """

    def get_queryset(self):
        """
        Returns all boards where the authenticated user is the owner
        or a member.
        """

        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the request method.
        """

        if self.request.method == "GET":
            return BoardListSerializer
        return BoardCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new board and returns it in the board list response format.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        data = BoardListSerializer(board).data
        return Response(data, status=status.HTTP_201_CREATED)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating and deleting a single board.
    """

    queryset = Board.objects.all()
    lookup_url_kwarg = "board_id"
    permission_classes = [
        IsAuthenticated,
        IsBoardOwnerOrMember,
        IsBoardOwnerForDelete,
    ]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the request method.
        """

        if self.request.method == "GET":
            return BoardDetailSerializer
        return BoardCreateUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates a board and returns the updated board data.
        """

        board = self.get_object()
        serializer = self.get_serializer(
            board,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        data = BoardUpdateResponseSerializer(board).data
        return Response(data, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """
    Returns user data for an existing email address.
    """

    def get(self, request):
        """
        Returns user data for the email address provided as a query parameter.
        """
        
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = UserDataSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)