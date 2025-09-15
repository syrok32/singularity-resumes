from django.conf import settings
from django.db.models import QuerySet
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from student.models import InternshipApplication
from telegram_bot.models import TelegramProfile
import json


def _send_text(chat_id: int, text: str, reply_markup: dict | None = None):
    try:
        api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': str(chat_id), 'text': text}
        if reply_markup is not None:
            data['reply_markup'] = json.dumps(reply_markup, ensure_ascii=False)
        payload = urlencode(data).encode('utf-8')
        req = Request(api_url, data=payload)
        urlopen(req, timeout=5)
    except Exception:
        pass


def build_application_text(app: InternshipApplication) -> str:
    return (
        f"Эй, {app.student.full_name or app.student.user.email}!\n"
        f"Работодатель '{app.employer_name}' хочет вас на стажировку.\n"
        f"Заявка #{app.id}: {app.message}\n"
        f"Ответьте командами: /accept {app.id} или /reject {app.id}"
    )


def send_application_notification(app: InternshipApplication):
    text_for_student = build_application_text(app)
    if app.student.telegram_chat_id:
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ Принять", "callback_data": f"app:accept:{app.id}"},
                {"text": "❌ Отклонить", "callback_data": f"app:reject:{app.id}"}
            ]]
        }
        _send_text(app.student.telegram_chat_id, text_for_student, reply_markup=keyboard)

    moderators: QuerySet[TelegramProfile] = TelegramProfile.objects.filter(is_moderator=True).exclude(chat_id=None)
    mod_text = (
        f"Новая заявка #{app.id} для {app.student.full_name or app.student.user.email} от '{app.employer_name}'.\n"
        f"Текст: {app.message}\n"
        f"Модераторский ответ: /accept {app.id} или /reject {app.id}"
    )
    for prof in moderators:
        keyboard = {
            "inline_keyboard": [[
                {"text": "✅ Одобрить", "callback_data": f"mod:accept:{app.id}"},
                {"text": "❌ Отклонить", "callback_data": f"mod:reject:{app.id}"}
            ]]
        }
        _send_text(prof.chat_id, mod_text, reply_markup=keyboard)
