from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    AdminRegistrationView,
    AdminLoginView,
    BookListCreateView,
    BookDetailView,
    BookEditView,
    AllBooksView,
    AvailableBooksView,
    UserLoansView,
    BorrowBookView,
    ReturnBookView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),

    path('register-admin/', AdminRegistrationView.as_view(), name='admin-registration'),
    path('login-admin/', AdminLoginView.as_view(), name='admin-login'),

    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/edit/', BookEditView.as_view(), name='book-edit'),

    path('all-books/', AllBooksView.as_view(), name='all-books'),
    path('available-books/', AvailableBooksView.as_view(), name='available-books'),

    path('user-loans/', UserLoansView.as_view(), name='user-loans'),
    path('borrow-book/', BorrowBookView.as_view(), name='borrow-book'),
    path('return-book/', ReturnBookView.as_view(), name='return-book'),
]
