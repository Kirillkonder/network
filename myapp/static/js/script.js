document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки "Удалить"
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Предотвращаем отправку формы по умолчанию
            event.preventDefault();

            // Показываем окно подтверждения
            const confirmation = confirm("Вы уверены, что хотите удалить этого друга?");

            if (confirmation) {
                // Если пользователь подтвердил, отправляем форму
                this.closest('form').submit();
            }
        });
    });
});