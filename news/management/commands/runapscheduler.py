import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Предполагается, что у вас есть модель Post с датой добавления и связью с категориями
from myapp.models import Post  # замените на ваш реальный путь к модели

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)

    # Получите все новые статьи за последнюю неделю
    new_posts = Post.objects.filter(created_at__gte=one_week_ago, created_at__lte=now)

    # Собираем уникальных подписчиков из всех категорий этих статей
    subscribers_emails = set()
    for post in new_posts:
        categories = post.postCategory.all()
        for category in categories:
            for user in category.subscribers.all():
                subscribers_emails.add(user.email)

    # Отправляем письма каждому подписчику
    for email in subscribers_emails:
        # Получите все статьи для этого подписчика
        user_posts = Post.objects.filter(
            postCategory__subscribers__email=email,
            created_at__gte=one_week_ago,
            created_at__lte=now
        ).distinct()

        if not user_posts:
            continue  # если у пользователя нет новых статей, пропускаем

        # Формируем HTML контент
        html_content = render_to_string(
            'weekly_newsletter.html',
            {
                'posts': user_posts,
            }
        )

        # Создаём и отправляем письмо
        email_message = EmailMultiAlternatives(
            subject='Новые статьи за неделю',
            from_email='andalsulekbaevaa@yandex.ru',
            to=[email],
        )
        email_message.attach_alternative(html_content, "text/html")
        try:
            email_message.send()
            logger.info(f"Отправлено письмо на {email}")
        except Exception as e:
            logger.error(f"Ошибка при отправке письма на {email}: {e}")


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Запускает планировщик задач APScheduler."

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Задача для еженедельной рассылки
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача: send_weekly_newsletter.")

        # Очистка устаревших задач каждую неделю
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="05"),
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