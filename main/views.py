from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Book, Author, Review
import bcrypt

# Create your views here.
def index(request):
    return render(request, 'index.html')

# localhost:8000/create_user
def create_user(request):
    if request.method == "POST":
        errors = User.objects.registration_validator(request.POST)

        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/')
        #print(request.POST['password'])
        
        #below var could be anything
        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        #print(hash_pw) #just to see what it prints in the terminal
        
        new_user = User.objects.create(
            name = request.POST['name'],
            alias = request.POST['alias'],
            email = request.POST['email'],
            password = hash_pw #whatever var you call it up above
        )
        request.session['logged_user'] = new_user.id

        return redirect('/user/dashboard')
    return redirect('/')
    # localhost:8000/dashboard

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email = request.POST['email'])

        if user:
            log_user = user[0]
            
            if bcrypt.checkpw(request.POST['password'].encode(), log_user.password.encode()):
                request.session['logged_user'] = log_user.id
                return redirect('/user/dashboard')
        messages.error(request, "Email or password are incorrect")

    return redirect("/")

def dashboard(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'all_books': Book.objects.all(),
        'recent_reviews': Review.objects.order_by('-created_at')[:3]
    }
    return render(request, 'dashboard.html', context)

def create_book(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    if request.method == 'POST':
        book_errors= Book.objects.book_validator(request.POST)
        review_errors= Review.objects.review_validator(request.POST)
        errors= list(book_errors.values())+list(review_errors.values())

        if request.POST['author_dropdown'] == "-1": #value is coming from value in the select option value in add_book.html
            if request.POST['author_name'] == "":
                messages.error(request, "Please either choose an author from the dropdown or create a new one")
            else:
                author_errors= Author.objects.author_validator(request.POST)
                errors+= list(author_errors.values())

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('/book/book_form')

        if request.POST['author_dropdown'] == "-1":
            author = Author.objects.create(name= request.POST['author_name'])
        else:
            author = Author.objects.get(id = request.POST['author_dropdown'])
        
        this_book= Book.objects.create(title= request.POST['title'])
        user= User.objects.get(id=request.session['logged_user'])
        review= Review.objects.create(content= request.POST['content'], rating= int(request.POST['rating']), book_reviewed= this_book, user_review= user)
        this_book.authors.add(author)
        return redirect(f'/book/{this_book.id}')
    return redirect('/book/book_form')

def book_form(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    context = {
        'authors': Author.objects.all()
    }
    return render(request, 'add_book.html', context)

def show_book(request, book_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    context = {
        'book': Book.objects.get(id=book_id)
    }
    return render(request, 'one_book.html', context)

def add_review(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    if request.method == 'POST':

        errors= Review.objects.review_validator(request.POST)
        book= Book.objects.get(id=request.POST['book_reviewed'])

        if errors:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect(f'/book/{book.id}')
        
        user= User.objects.get(id=request.session['logged_user'])
        review= Review.objects.create(content= request.POST['content'], rating= int(request.POST['rating']), book_reviewed= book, user_review= user)

        return redirect(f'/book/{book.id}')

def logout(request):
    request.session.flush()
    return redirect('/')

def user_page(request, user_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    user= User.objects.get(id=user_id)

    context= {
        'one_user': user
    }
    return render(request, 'user_page.html', context)

def delete_review(request, review_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    review= Review.objects.get(id=review_id)
    review.delete()
    return redirect(f'/book/{review.book_reviewed.id}')