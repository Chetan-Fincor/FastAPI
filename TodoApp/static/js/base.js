// ===============================
// TODO CREATE
// ===============================
const todoForm = document.getElementById('todoForm');

if (todoForm) {
    todoForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(todoForm);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: false
        };

        try {
            const response = await fetch('/todos/todo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                todoForm.reset();
                window.location.href = '/todos/todo-page';
            } else {
                const err = await response.json();
                alert(err.detail || "Error creating todo");
            }
        } catch (error) {
            console.error(error);
            alert("Something went wrong");
        }
    });
}


// ===============================
// TODO EDIT
// ===============================
const editTodoForm = document.getElementById('editTodoForm');

if (editTodoForm) {
    editTodoForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(editTodoForm);
        const data = Object.fromEntries(formData.entries());

        const todoId = window.location.pathname.split('/').pop();

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: document.getElementById('complete').checked
        };

        try {
            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/todos/todo-page';
            } else {
                const err = await response.json();
                alert(err.detail || "Error updating todo");
            }
        } catch (error) {
            console.error(error);
            alert("Something went wrong");
        }
    });
}


// ===============================
// TODO DELETE
// ===============================
const deleteButton = document.getElementById('deleteButton');

if (deleteButton) {
    deleteButton.addEventListener('click', async () => {
        const todoId = window.location.pathname.split('/').pop();

        try {
            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                window.location.href = '/todos/todo-page';
            } else {
                const err = await response.json();
                alert(err.detail || "Error deleting todo");
            }
        } catch (error) {
            console.error(error);
            alert("Something went wrong");
        }
    });
}


// ===============================
// LOGIN
// ===============================
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const payload = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
        payload.append(key, value);
    }

    const response = await fetch('/auth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: payload.toString(),
        redirect: "follow"
    });

    if (response.redirected) {
        window.location.href = response.url;
    } else {
        const err = await response.json();
        alert(err.detail);
    }
});


// ===============================
// REGISTER
// ===============================
const registerForm = document.getElementById('registerForm');

if (registerForm) {
    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.firstname,
            last_name: data.lastname,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password
        };

        try {
            const response = await fetch('/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/auth/login-page';
            } else {
                const err = await response.json();
                alert(err.detail || "Registration failed");
            }
        } catch (error) {
            console.error(error);
            alert("Something went wrong");
        }
    });
}


// ===============================
// LOGOUT (SAFE VERSION)
// ===============================
function logout() {
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.href = '/auth/login-page';
}


// ===============================
// COOKIE HELPER (optional use only)
// ===============================
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}