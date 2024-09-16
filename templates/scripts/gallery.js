document.addEventListener('DOMContentLoaded', () => {
    // Функция для получения данных о постах
    fetch('/posts')  // Этот API должен возвращать список всех JSON-файлов в папке posts
        .then(response => response.json())
        .then(files => {
            const galleryContainer = document.getElementById('gallery');  // Контейнер для изображений

            // Для каждого файла загружаем его содержимое
            files.forEach(file => {
                const postId = file.replace('.json', '');  // Убираем расширение .json

                // Запрашиваем данные по идентификатору (без расширения .json)
                fetch(`/get_post_data/${postId}`)
                    .then(response => response.json())
                    .then(post => {
                        // Создаём элемент для каждого изображения
                        const galleryItem = document.createElement('div');
                        galleryItem.className = 'gallery-item';

                        // Создаём изображение и задаем его параметры
                        const img = document.createElement('img');
                        img.src = `/${post.image_url}`;  // URL изображения из JSON-файла
                        img.alt = post.name;
                        img.className = 'post-image';

                        // Добавляем событие клика на изображение
                        img.addEventListener('click', () => {
                            window.location.href = `/posts/${post.id}`;  // Переход на страницу поста по id
                        });

                        // Добавляем изображение в контейнер
                        galleryItem.appendChild(img);
                        galleryContainer.appendChild(galleryItem);
                    })
                    .catch(error => console.error('Error loading post:', error));
            });
        })
        .catch(error => console.error('Error fetching posts list:', error));
});
