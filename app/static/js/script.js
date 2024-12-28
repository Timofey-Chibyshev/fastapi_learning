async function loginFunction(event) {
    event.preventDefault();

    const form = document.getElementById('login-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (!validateLoginForm()) {
        return;
    }

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayFormErrors(errorData.detail || "Ошибка входа");
            return;
        }

        const result = await response.json();
        if (result.message) {
            alert(result.message);
            window.location.href = '/pages/profile';
        } else {
            alert(result.message || 'Неизвестная ошибка');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при входе. Проверьте соединение с сервером.');
    }
}

async function logoutFunction() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            window.location.href = '/pages/login';
        } else {
            const errorData = await response.json();
            console.error('Ошибка при выходе:', errorData.message || response.statusText);
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
    }
}

async function regFunction(event) {
    event.preventDefault();

    const form = document.getElementById('registration-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (!validateRegistrationForm()) {
        return;
    }

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayFormErrors(errorData.detail || "Ошибка регистрации");
            return;
        }

        const result = await response.json();
        if (result.message) {
            window.location.href = '/pages/login';
        } else {
            alert(result.message || 'Неизвестная ошибка');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при регистрации. Попробуйте снова.');
    }
}

function validateField(field) {
    const value = document.getElementById(field)?.value.trim();
    const errorElement = document.getElementById(`${field}-error`);

    if (!errorElement) {
        console.warn(`Элемент для отображения ошибки не найден: ${field}-error`);
        return false;
    }

    errorElement.textContent = ''; // Очистка предыдущего сообщения
    let isValid = true;

    if (field === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            errorElement.textContent = 'Введите корректный email. Например: example@example.com';
            isValid = false;
        }
    } else if (field === 'password') {
        if (value.length < 6) {
            errorElement.textContent = 'Пароль должен быть не менее 6 символов.';
            isValid = false;
        } else if (!/\d/.test(value)) {
            errorElement.textContent = 'Пароль должен содержать хотя бы одну цифру.';
            isValid = false;
        } else if (!/[A-Za-z]/.test(value)) {
            errorElement.textContent = 'Пароль должен содержать хотя бы одну букву.';
            isValid = false;
        }
    }

    return isValid;
}

function validateLoginForm() {
    const fields = ['email', 'password'];
    let isFormValid = true;

    fields.forEach((field) => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

function validateRegistrationForm() {
    const fields = ['email', 'password', 'phone_number', 'first_name', 'last_name'];
    let isFormValid = true;

    fields.forEach((field) => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

document.addEventListener('DOMContentLoaded', function () {
    addInputListeners();

    document.getElementById('login-form').addEventListener('submit', async function (event) {
        event.preventDefault(); // Остановить стандартное поведение формы
        clearAllErrors(); // Очистка всех ошибок перед проверкой

        if (!validateLoginForm()) {
            return; // Завершаем обработку, если форма невалидна
        }
        await loginFunction(event); // Выполнить логику входа
    });

    document.getElementById('registration-form').addEventListener('submit', async function (event) {
        event.preventDefault(); // Остановить стандартное поведение формы
        clearAllErrors(); // Очистка всех ошибок перед проверкой

        if (!validateRegistrationForm()) {
            return; // Завершаем обработку, если форма невалидна
        }
        await regFunction(event); // Выполнить логику регистрации
    });
});

function clearAllErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(error => error.textContent = '');
}

function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), delay);
    };
}

function addInputListeners() {
    document.getElementById('email').addEventListener('input', debounce(() => validateField('email'), 300));
    document.getElementById('password').addEventListener('input', debounce(() => validateField('password'), 300));
    if (document.getElementById('phone_number')) {
        document.getElementById('phone_number').addEventListener('input', debounce(() => validateField('phone_number'), 300));
    }
    if (document.getElementById('first_name')) {
        document.getElementById('first_name').addEventListener('input', debounce(() => validateField('first_name'), 300));
    }
    if (document.getElementById('last_name')) {
        document.getElementById('last_name').addEventListener('input', debounce(() => validateField('last_name'), 300));
    }
}

function displayFormErrors(errors) {
    const errorContainer = document.querySelector('.error-container');
    errorContainer.innerHTML = '';

    if (typeof errors === 'string') {
        const errorElement = document.createElement('p');
        errorElement.textContent = errors;
        errorElement.style.color = 'red';
        errorContainer.appendChild(errorElement);
    } else if (Array.isArray(errors)) {
        errors.forEach(error => {
            const errorElement = document.createElement('p');
            errorElement.textContent = error.msg || error;
            errorElement.style.color = 'red';
            errorContainer.appendChild(errorElement);
        });
    }
}

