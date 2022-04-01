
document.addEventListener('DOMContentLoaded', function() {

      // получим кнопку id="btn" с помощью которой будем открывать модальное окно
    const btn = document.querySelector('#btn');
      // активируем контент id="modal" как модальное окно
      const modal = new bootstrap.Modal(document.querySelector('#modal'));
      // при нажатии на кнопку
      btn.addEventListener('click', function() {
        // открывает модальное окно
        modal.show();
      });

    });
