from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Quiz, Question, Student, QuizResult

# Home Page
def home(request):
    quizzes = Quiz.objects.all()
    return render(request, "quiz_app/home.html", {"quizzes": quizzes})

# User Registration
def user_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("register")
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
    
    return render(request, "quiz_app/register.html")

# User Login
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "quiz_app/login.html")

# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

# Create a new quiz (Only for logged-in users)
@login_required
def create_quiz(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a quiz!")
        return redirect("login")

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        time_limit = request.POST["time_limit"]
        password = request.POST["password"]

        quiz = Quiz.objects.create(user = request.user, title=title, description=description, time_limit=time_limit, quiz_password=password)
        return redirect("add_questions", quiz_id=quiz.id)

    return render(request, "quiz_app/create_quiz.html")

# Add Questions
@login_required
def add_questions(request, quiz_id): 
    quiz = get_object_or_404(Quiz, id=quiz_id)
    total_questions = Question.objects.filter(quiz=quiz).count()

    if request.method == "POST":
        question_text = request.POST["question_text"]
        option1 = request.POST["option1"]
        option2 = request.POST["option2"]
        option3 = request.POST["option3"]
        option4 = request.POST["option4"]
        correct_answer = request.POST["correct_answer"]

        Question.objects.create(
            quiz=quiz,
            text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_answer
        )

        messages.success(request, "Question added successfully!")
        return redirect("add_questions", quiz_id=quiz.id)
 
    return render(request, "quiz_app/add_questions.html", {"quiz": quiz, 'total_questions': total_questions})

import random

# Show quiz details
def quiz_detail(request, quiz_id, quiz_pass):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())
    random.shuffle(questions)
    return render(request, "quiz_app/quiz_detail.html", {"quiz": quiz, 'questions': questions})


def submit_quiz(request, quiz_id):
    """Processes quiz submission, calculates score, and saves results."""
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        student_id = request.session.get('student_id')

        if not student_id:
            return JsonResponse({"error": "Student not found in session"}, status=400)

        student = get_object_or_404(Student, id=student_id)

        # Check if student already submitted the quiz
        if QuizResult.objects.filter(student=student, quiz=quiz).exists():
            return redirect('thank_you')

        # Calculate score
        questions = Question.objects.filter(quiz=quiz)
        score = 0

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer and user_answer == question.correct_option:
                score += 1

        # Get time taken from frontend
        time_taken = int(request.POST.get('time_taken', 0))  # Default to 0 if missing

        # Save result
        QuizResult.objects.create(
            student=student,
            quiz=quiz,
            score=score,
            total_questions=questions.count(),
            time_taken=time_taken
        )

        return redirect('thank_you')

    return JsonResponse({"error": "Invalid request"}, status=400)


def start_quiz(request, quiz_id):
    """Redirects users to student details page before the quiz."""
    return redirect('student_details', quiz_id=quiz_id)


def student_details(request, quiz_id):
    """Collects student information and prevents duplicate attempts."""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        enrollment = request.POST.get("enrollment")
        name = request.POST.get("name")
        branch = request.POST.get("branch")
        year = request.POST.get("year")
        email = request.POST.get("email")

        # Check if the student has already taken the quiz
        existing_student = Student.objects.filter(enrollment=enrollment).first()
        if existing_student:
            existing_result = QuizResult.objects.filter(student = existing_student, quiz=quiz).first()
            print(existing_student)
            print(existing_result)
            if existing_result:
                messages.warning(request, "You have already taken this quiz. Please try another quiz.")
                return redirect("quiz_already_taken")  # Redirect to a page saying they already took it.

        # If not taken, create student and store in session
        student = Student.objects.create(enrollment = enrollment, name=name, branch = branch, year = year, email=email, quiz=quiz)
        request.session["student_id"] = student.id
        return redirect("quiz_password", quiz_id=quiz.id)  # Redirect to the password page

    return render(request, "student_details.html", {"quiz": quiz})

def quiz_already_taken(request):
    """Displays a message if the student has already taken the quiz."""
    return render(request, "quiz_app/quiz_already_taken.html")


def quiz_password(request, quiz_id):
    """Validates quiz password before allowing the user to start."""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        entered_password = request.POST.get('password')
        if entered_password == quiz.quiz_password:
            return redirect('quiz_detail', quiz_id=quiz.id, quiz_pass = quiz.quiz_password)  # Redirect to quiz start

    return render(request, 'quiz_password.html', {'quiz': quiz})

def thank_you(request):
    return render(request, 'thank_you.html')

@login_required
def edit_question(request, question_id):
    """Allows updating an existing question."""
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        question.text = request.POST.get("text")
        question.option1 = request.POST.get("option1")
        question.option2 = request.POST.get("option2")
        question.option3 = request.POST.get("option3")
        question.option4 = request.POST.get("option4")
        question.correct_option = request.POST.get("correct_option")

        question.save()
        messages.success(request, "Question updated successfully!")
        return redirect("quiz_questions", quiz_id=question.quiz.id)

    return render(request, "quiz_app/edit_question.html", {"question": question})

@login_required
def delete_question(request, question_id):
    """Deletes a question after confirmation."""
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id

    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect("quiz_questions", quiz_id=quiz_id)

    return render(request, "quiz_app/delete_question.html", {"question": question})


@login_required
def quiz_questions(request, quiz_id):
    """Displays questions for a given quiz, allowing the creator to manage them."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    # Ensure only the creator can manage questions
    if request.user != quiz.user:
        return redirect('home')  # Redirect if not authorized

    return render(request, 'quiz_app/manage_questions.html', {'quiz': quiz, 'questions': questions})


@login_required
def delete_quiz(request, quiz_id): 
    """Deletes a quiz if the user is the creator."""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure only the creator can delete the quiz
    if request.user == quiz.user:
        quiz.delete()
        return redirect('home')  # Redirect to home after deletion

    return redirect('home')  # Redirect unauthorized users



@login_required
def quiz_results(request, quiz_id):
    """Allows quiz creator to see student results."""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure only the quiz creator can access results
    if request.user != quiz.user:
        return render(request, 'quiz_app/not_allowed.html')

    results = QuizResult.objects.filter(quiz=quiz).order_by('-score', 'time_taken')

    return render(request, 'quiz_app/quiz_results.html', {'quiz': quiz, 'results': results})
