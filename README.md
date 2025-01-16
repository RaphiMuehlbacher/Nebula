# Nebula

**Nebula** is a lightweight web server framework designed to simplify web application development with Python. It offers a powerful yet easy-to-use interface for building robust web applications.

## Features

 - **Routing**: Simple and dynamic URL routing.
 - **Views**: Supports both function-based and class-based views.
 - **Static Files**: Effortless serving of static files.
 - **Auto-Reloading**: Automatically reloads the server on code changes.
 - **ORM**: Custom-built ORM for database interactions.
 - **Models**: Easily define and manage database schemas.
 - **Database Integration**: Pre-configured for SQLite3 support.
 - **API Serialization**: Quickly build APIs with model serialization.

## Installation
### Recommended Installation
To install the latest version of Nebula, use the following commands:

You can also perform common database operations like querying, filtering, and updating with a simple API:
```bash
# Clone the repository
git clone https://github.com/RaphiMuehlbacher/Nebula.git
cd nebula

# Install the package
pip install .
```

Once installed, you can safely delete the cloned `nebula` folder.


### Alternative Installation (Not Recommended)
Install from PyPI (only updated on major releases):
```bash
pip install nebula-web
```


## Creating a new project
To create a new project using Nebula, run the following command:
````bash
nebula-admin startproject {project-name}
````
This will create a new directory and a manage.py file in the root directory.
```plaintext               
root-folder/
├── project-name/           # Your project directory
│   ├── __init__.py         
│   ├── models.py           # Define database schemas   
│   ├── serializers.py      # API serializers for models
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   └── views.py            # Views for handling requests
└── manage.py               # Command-line utility
```
## Running the Server
By default, the server starts at http://127.0.0.1:8080/. You can customize the host and port using the --host and --port arguments:
```bash 
nebula-admin runserver [--host <ip>] [--port <port>]
```

# Features in Detail

### Automatic Server Restart
Nebula uses the **Watchdog** library to monitor file changes. When changes are detected, the server automatically restarts.

### ORM and Models
Nebula includes a custom-built ORM for database interactions. Define schemas easily using models:
```python
# models.py
from nebula import models

class User(models.Model):
    username = models.CharField()
    age = models.IntegerField()
```

You can also perform common database operations like querying, filtering, and updating with a simple API:

```python
# Query all users
users = User.objects.all()

# Filter users by age and username
adults = User.objects.filter(age=18, username='Raphael')

# Update a user
user = User.objects.get(id=1)
user.age = 30
user.save()
```

### Serializer
Create APIs effortlessly by serializing models. Define serializers to convert model instances to JSON:

```python
# serializers.py
from nebula.serializers import Serializer
from .model import User

class UserSerializer(Serializer):
    class Meta:
        model = User
        fields = ['username', 'age']
```

Serializers can also validate input data when creating or updating models:

```python
serializer = UserSerializer(data={"username": "Alice", "age": 25})
if serializer.is_valid():
    user = serializer.save()
```

### Routing
Nebula's routing system allows you to define URL patterns dynamically. Configure routes in the `urls.py` file:
```python 
#urls.py
from nebula.urls import path
from nebula.views import as_view
from .views import home_view, about_view, user_detail, UserListView

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('users/<age>', users_filter, name='users_by_age'),
    path('users/<user_id>', user_detail, name='user_detail'),
    path('users/', UserListView.as_view(), name='user_list')
]
```

### Views
Nebula supports both function-based and class-based views for handling HTTP requests.
```python
# views.py
from nebula.http import HTTPResponse, JsonResponse
from nebula.utils import render
from .serializers import UserSerializer 
from .models import User

# Simple response view
def home_view(request):
    return HTTPResponse("Welcome to Nebula!")

# Render templates
def about(request):
    return render("about.html")

# Filter and display users by age
def users_filter(request, age):
    users = User.objects.filter(age=age)
    return render('users.html', context={'users': users})
    
# Handle specific user detail
def user_view(request, user_id):
    user = User.objects.get(id=user_id)
    return render('user.html', context={'user': user})

# Create a new user
def create_user(request):
    if request.method == 'POST':
        form_data = request.form_data
        user = User(username=form_data['username'], age=form_data['age'])
        user.save()
        return HTTPResponse('User created successfully')
    return HTTPResponse('Invalid method', 404)
```

#### Class-Based Views
```python
class UserListView(ApiView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(instance=users, many=True)
        return JsonResponse(serializer.to_representation(users))
    
    def post(self, request, *args, **kwarg):
        data = request.form_data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
```
