import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.models import Site

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """Отправка еженедельной рассылки подписчикам по категориям."""
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)

    # Берем все посты за неделю
    new_posts = Post.objects.filter(dateCreation__gte=one_week_ago)

    if not new_posts.exists():
        logger.info("Нет новых постов за неделю — рассылка не требуется.")
        return

    # Получаем текущий домен из django.contrib.sites
    current_site = Site.objects.get_current()
    domain = current_site.domain  # например 127.0.0.1:8000

    # Собираем всех подписчиков, у которых есть новые статьи
    subscribers_emails = set()
    for post in new_posts:
        for category in post.postCategory.all():
            for user in category.subscribers.all():
                subscribers_emails.add(user.email)

    for email in subscribers_emails:
        # Фильтруем посты по подпискам конкретного пользователя
        user_posts = Post.objects.filter(
            postCategory__subscribers__email=email,
            dateCreation__gte=one_week_ago
        ).distinct()

        if not user_posts:
            continue

        # Формируем список постов с абсолютными ссылками
        posts_with_urls = []
        for post in user_posts:
            full_url = f"http://{domain}{reverse('post_read', args=[post.pk])}"
            posts_with_urls.append({
                'title': post.title,
                'text': post.text,
                'dateCreation': post.dateCreation,
                'url': full_url,
            })

        # Рендерим шаблон
        html_content = render_to_string(
            'weekly_newsletter.html',  # ← твой шаблон
            {
                'posts': posts_with_urls,
            }
        )

        # Отправляем письмо
        email_message = EmailMultiAlternatives(
            subject='Новые статьи за неделю',
            from_email='andalsulekbaevaa@yandex.ru',
            to=[email],
        )
        email_message.attach_alternative(html_content, "text/html")

        try:
            email_message.send()
            logger.info(f"Письмо отправлено на {email}")
        except Exception as e:
            logger.error(f"Ошибка при отправке письма на {email}: {e}")


def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи о выполнении задач APScheduler (старше недели)."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Запускает планировщик APScheduler для еженедельной рассылки."

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Рассылка по понедельникам в 8:00 утра
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(day_of_week="mon", hour="8", minute="0"),
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача: send_weekly_newsletter.")

        # Очистка старых записей APScheduler
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="8", minute="5"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача: delete_old_job_executions.")

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик остановлен успешно!")