from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import User, Book, Loan
from .serializers import UserSerializer, BookSerializer, LoanSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data['username']
        password = data['password']
        name = data.get('name', '')

        user = User.objects.create(username=username, name=name,)
        user.set_password(password)
        user.save()

        serializer = UserSerializer(user)
        return Response({'message': 'User created successfully', 'user': serializer.data},
                        status=status.HTTP_201_CREATED)



class AdminRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data['username']
        password = data['password']
        is_admin = True
        name = data.get('name', '')

        user = User.objects.create(
            username=username,
            is_staff=is_admin,
            name=name,
        )
        user.set_password(password)
        user.is_admin = True
        user.save()

        serializer = UserSerializer(user)
        return Response({'message': 'Admin created successfully', 'admin': serializer.data},
                        status=status.HTTP_201_CREATED)



class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data['username']
        password = data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            context = {'message': f'Logged in as {username}', 'csrf_token': get_token(request)}
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class AdminLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data['username']
        password = data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_admin:
            login(request, user)
            context = {'message': f'Logged in as admin: {username}', 'csrf_token': get_token(request)}
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid admin credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Book.objects.all()
        else:
            return Book.objects.filter(loan__isnull=True)

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

class BookEditView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data

        title = data['title']
        isbn = data['isbn']
        author = data['author']

        book = Book.objects.create(
            title=title,
            isbn=isbn,
            author=author,
        )

        return Response({'message': 'Book created successfully'}, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        data = request.data
        book_id = kwargs.get('pk')
        book = get_object_or_404(Book, pk=book_id)

        book.title = data.get('title', book.title)
        book.isbn = data.get('isbn', book.isbn)
        book.author = data.get('author', book.author)
        book.save()

        return Response({'message': 'Book updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        book_id = kwargs.get('pk')
        book = get_object_or_404(Book, pk=book_id)
        book.delete()

        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)

class AllBooksView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

class AvailableBooksView(generics.ListAPIView):
    queryset = Book.objects.filter(loan__isnull=True)
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

class UserLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Loan.objects.none()

        return Loan.objects.filter(user=user)

class BorrowBookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')

        if user.is_admin:
            return Response({'message': 'Admins are not allowed to borrow books'}, status=status.HTTP_403_FORBIDDEN)

        if Loan.objects.filter(user=user, book_id=book_id, returned=False).exists():
            return Response({'message': 'You have already borrowed this book'}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, pk=book_id, loan__isnull=True)

        loan = Loan.objects.create(user=user, book=book)

        return Response({'message': 'Book borrowed successfully'}, status=status.HTTP_200_OK)

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Loan, Book

class ReturnBookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')

        loan = get_object_or_404(Loan, user=user, book_id=book_id, returned=False)

        if user.is_admin:
            return Response({'message': 'Admins are not allowed to return books'}, status=status.HTTP_403_FORBIDDEN)

        loan.returned = True
        loan.save()

        book = loan.book
        book.loan = None
        book.save()

        loan.delete()

        return Response({'message': 'Book returned successfully'}, status=status.HTTP_200_OK)