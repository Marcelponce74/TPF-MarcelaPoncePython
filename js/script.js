function validarEnviar() {
    // Obtener los campos del formulario
    const nombre = document.getElementById('nombre');
    const apellido = document.getElementById('apellido');
    const email = document.getElementById('email');
    const telefono = document.getElementById('telefono');
    const mensaje = document.getElementById('mensaje');
    const warning = document.getElementById('warning');

    // Limpiar mensaje de advertencia
    warning.innerHTML = '';

    // Validar el nombre
    if (nombre.value.trim() === '') {
        warning.innerHTML = 'Tiene que escribir su nombre';
        nombre.focus();
        return;
    }

    // Validar el apellido
    if (apellido.value.trim() === '') {
        warning.innerHTML = 'Tiene que escribir su apellido';
        apellido.focus();
        return;
    }

    // Validar el email
    if (email.value.trim() === '') {
        warning.innerHTML = 'Tiene que escribir su email';
        email.focus();
        return;
    } else if (!validateEmail(email.value)) {
        warning.innerHTML = 'El email no es válido';
        email.focus();
        return;
    }

    // Validar el teléfono
    if (telefono.value.trim() === '') {
        warning.innerHTML = 'Tiene que escribir su teléfono';
        telefono.focus();
        return;
    } else if (!validarEntero(telefono.value)) {
        warning.innerHTML = 'El teléfono debe ser un número';
        telefono.focus();
        return;
    }

    // Validar el mensaje
    if (mensaje.value.trim() === '') {
        warning.innerHTML = 'Tiene que escribir su mensaje';
        mensaje.focus();
        return;
    }

    // Validar las actividades
    const actividades = document.querySelectorAll('.actividadCheckbox');
    let actividadSeleccionada = false;
    actividades.forEach(checkbox => {
        if (checkbox.checked) {
            actividadSeleccionada = true;
        }
    });

    if (!actividadSeleccionada) {
        warning.innerHTML = 'Debe seleccionar al menos una actividad';
        return;
    }

     // Si todo es válido, mostrar mensaje de éxito
     warning.innerHTML = 'El formulario ha sido enviado correctamente';
     warning.classList.remove('warning');
     warning.classList.add('success');
 
     // Limpiar campos del formulario
     document.getElementById('form').reset();
 }


function validarEntero(valor) {
    valor = parseInt(valor);
    return !isNaN(valor);
}

function validateEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase());
}
