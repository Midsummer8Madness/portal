from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.urls import reverse

@receiver(m2m_changed, sender=Post.postCategory.through)
def send_notification_on_category_change(sender, instance, action, **kwargs):
    print(f"Action: {action}")  # Отладка: вывод действия
    # Проверка действия (если категории были добавлены)
    if action == 'post_add':  # Если категории были добавлены
        post = instance
        print(f"Обработка поста: {post.title} (ID: {post.id})")

        current_site = Site.objects.get_current()
        domain = current_site.domain

        # Формируем полный URL с http:// и портом, как в админке
        full_url = f"http://{domain}{reverse('post_read', args=[post.pk])}"

        # Отладка: вывод информации о посте
        categories = post.postCategory.all()
        print(f"Категории поста: {[category.name for category in categories]}")  # Отладка: список категорий
        for category in categories:
            print(f"Обработка категории: {category.name} (ID: {category.id})")  # Отладка: категория
            subscribers = category.subscribers.all()
            print(f"Подписчики категории: {[user.email for user in subscribers]}")  # Отладка: подписчики
            for user in subscribers:
                print(f"Обработка пользователя: {user.email}")  # Отладка: пользователь
                try:
                    email = EmailMultiAlternatives(
                        subject=post.title,
                        from_email='andalsulekbaevaa@yandex.ru',
                        to=[user.email],
                    )
                    print(f"Создано письмо для {user.email}")  # Отладка: создание письма
                    html_content = render_to_string(
                        'message_new_post.html',
                        {
                            'post': post,
                            'user': user,
                            'full_url': full_url,
                        }
                    )
                    print(f"HTML контент сформирован для {user.email}")  # Отладка: HTML контент
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    print(f"Письмо отправлено {user.email}")
                except Exception as e:
                    print(f"Ошибка при отправке письма {user.email}: {e}")