# from django.core.management.base import BaseCommand
# from site_app.telegram_bot import bot
# from django.conf import settings
#
# class Command(BaseCommand):
#     help = 'Запускает Telegram бота'
#
#     def handle(self, *args, **options):
#         self.stdout.write("Бот запущен...")
#         bot.polling(none_stop=True)
#
# from django.core.management.base import BaseCommand
# from site_app.telegram_bot import bot  # Проверьте путь!
#
# class Command(BaseCommand):
#     help = 'Запускает Telegram бота'
#
#     def handle(self, *args, **options):
#         self.stdout.write("Бот запущен и готов к работе!")
#         bot.polling(none_stop=True, interval=1)

from django.core.management.base import BaseCommand
from site_app.telegram_bot import bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write("Бот запущен и готов к работе!")
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))