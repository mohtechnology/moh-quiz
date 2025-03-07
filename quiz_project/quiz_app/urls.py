from django.urls import path
from .views import (
    home, create_quiz, add_questions, quiz_detail, quiz_password, start_quiz, submit_quiz,
    user_register, user_login, user_logout, student_details, thank_you, quiz_results, quiz_already_taken,
    edit_question, delete_question, quiz_questions, delete_quiz
)

urlpatterns = [
    path('', home, name='home'),  # Home page listing all quizzes
    path('register/', user_register, name='register'),  # User Registration 
    path('login/', user_login, name='login'),  # User Login
    path('logout/', user_logout, name='logout'),  # User Logout
    path('create/', create_quiz, name='create_quiz'),  # Create quiz
    path('add_questions/<int:quiz_id>/', add_questions, name='add_questions'),  # Add questions
    path('quiz/<int:quiz_id>/student/', student_details, name='student_details'),
    path('quiz/<int:quiz_id>/<str:quiz_pass>', quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/password/', quiz_password, name='quiz_password'),  # Quiz password check
    path('quiz/<int:quiz_id>/start/', start_quiz, name='start_quiz'),  # Start quiz
    path('quiz/<int:quiz_id>/submit/', submit_quiz, name='submit_quiz'),  # Submit quiz
    path('thank_you/', thank_you, name='thank_you'),
    path('quiz/<int:quiz_id>/results/', quiz_results, name='quiz_results'),
    path("quiz/already_taken/", quiz_already_taken, name="quiz_already_taken"),
    path("question/<int:question_id>/edit/", edit_question, name="edit_question"),
    path("quiz/<int:quiz_id>/questions/", quiz_questions, name="quiz_questions"),
    path("question/<int:question_id>/delete/", delete_question, name="delete_question"),
    path("quiz/<int:quiz_id>/delete/", delete_quiz, name="delete_quiz"),
]
