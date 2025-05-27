# from django.contrib.auth import login
# from django.shortcuts import render, redirect
# from site_app.forms import RegisterForm, FeedbackForm
# from site_app.models import Feedback, Reservation
# from site_app.telegram_bot import bot
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# from django.contrib.contenttypes.models import ContentType
# from site_app.models import LikeDislike, Comment
# import json
# import logging
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
#
# def index(request):
#     return render(request, 'index.html', {
#         'reservations': Reservation.objects.annotate(
#             likes_count=...,
#             dislikes_count=...
#         )
#     })
#
# def register(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#
#             if settings.TELEGRAM_ADMIN_CHAT_ID:
#                 bot.send_message(
#                     settings.TELEGRAM_ADMIN_CHAT_ID,
#                     f"Новый пользователь: {user.username}\nEmail: {user.email}"
#                 )
#
#             login(request, user)
#             return redirect('profile')
#     else:
#         form = RegisterForm()
#     return render(request, 'register.html', {'form': form})
#
# def submit_feedback(request):
#     if request.method == 'POST':
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             feedback = form.save(commit=False)
#             feedback.user = request.user
#             feedback.source = 'WEB'
#             feedback.save()
#             return redirect('thank_you')
#     else:
#         form = FeedbackForm()
#     return render(request, 'feedback.html', {'form': form})
#
# logger = logging.getLogger(__name__)
#
# @require_POST
# @login_required
# def like_dislike(request):
#     try:
#         data = json.loads(request.body)
#         content_type = ContentType.objects.get(model=data['content_type'])
#         obj = content_type.get_object_for_this_type(pk=data['object_id'])
#
#         vote = 1 if data['action'] == 'like' else -1
#
#         like_dislike, created = LikeDislike.objects.get_or_create(
#             user=request.user,
#             content_type=content_type,
#             object_id=obj.id,
#             defaults={'vote': vote}
#         )
#
#         if not created:
#             if like_dislike.vote == vote:
#                 like_dislike.delete()
#             else:
#                 like_dislike.vote = vote
#                 like_dislike.save()
#
#         likes = obj.likes_dislikes.filter(vote=1).count()
#         dislikes = obj.likes_dislikes.filter(vote=-1).count()
#
#         return JsonResponse({
#             'success': True,
#             'likes': likes,
#             'dislikes': dislikes,
#             'object_id': obj.id
#         })
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=400)
#
# @require_POST
# @login_required
# def add_comment(request):
#     data = json.loads(request.body)
#     content_type = ContentType.objects.get(model=data['content_type'])
#     obj = content_type.get_object_for_this_type(pk=data['object_id'])
#
#     comment = Comment.objects.create(
#         user=request.user,
#         content_object=obj,
#         text=data['text']
#     )
#
#     # Отправка обновления через WebSocket
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "updates",
#         {
#             "type": "send_update",
#             "data": {
#                 "content_type": data['content_type'],
#                 "object_id": data['object_id'],
#                 "comment": {
#                     'id': comment.id,
#                     'text': comment.text,
#                     'username': comment.user.username,
#                     'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
#                 },
#                 "action": "new_comment"
#             }
#         }
#     )
#
#     return JsonResponse({
#         'success': True,
#         'comment': {
#             'id': comment.id,
#             'text': comment.text,
#             'username': comment.user.username,
#             'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
#         }
#     })
# хорший код

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from site_app.forms import RegisterForm, FeedbackForm
from site_app.models import Feedback, Reservation
from site_app.telegram_bot import bot
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
# from site_app.models import LikeDislike, Comment
from site_app.models import LikeDislike
import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# def index(request):
#     reservations = Reservation.objects.all().order_by('-created_at')
#     return render(request, 'index.html', {
#         'reservations': reservations
#     })

def index(request):
    reservations = Reservation.objects.annotate(
        likes_count=Count(
            'likes_dislikes',
            filter=Q(likes_dislikes__vote=LikeDislike.LIKE)
        ),
        dislikes_count=Count(
            'likes_dislikes',
            filter=Q(likes_dislikes__vote=LikeDislike.DISLIKE)
        )
    ).order_by('-created_at')

    return render(request, 'index.html', {
        'reservations': reservations
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            if settings.TELEGRAM_ADMIN_CHAT_ID:
                bot.send_message(
                    settings.TELEGRAM_ADMIN_CHAT_ID,
                    f"Новый пользователь: {user.username}\nEmail: {user.email}"
                )

            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.source = 'WEB'
            feedback.save()
            return redirect('thank_you')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})


logger = logging.getLogger(__name__)


@require_POST
@login_required
def like_dislike(request):
    try:
        data = json.loads(request.body)
        content_type = ContentType.objects.get(model=data['content_type'])
        obj = content_type.get_object_for_this_type(pk=data['object_id'])

        vote = LikeDislike.LIKE if data['action'] == 'like' else LikeDislike.DISLIKE

        # Логирование перед созданием
        print(f"Creating vote: user={request.user.pk}, object={obj.pk}, vote={vote}")

        like_dislike, created = LikeDislike.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.id,
            defaults={'vote': vote}
        )

        if not created:
            if like_dislike.vote == vote:
                like_dislike.delete()
                action = 'removed'
            else:
                like_dislike.vote = vote
                like_dislike.save()
                action = 'changed'
        else:
            action = 'added'

        # Получаем актуальные счетчики
        likes = obj.likes_dislikes.filter(vote=LikeDislike.LIKE).count()
        dislikes = obj.likes_dislikes.filter(vote=LikeDislike.DISLIKE).count()

        # Отправка обновления через WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "updates",
            {
                "type": "send_update",
                "data": {
                    "content_type": data['content_type'],
                    "object_id": data['object_id'],
                    "likes": likes,
                    "dislikes": dislikes,
                    "action": "vote_" + action
                }
            }
        )

        return JsonResponse({
            'success': True,
            'likes': likes,
            'dislikes': dislikes,
            'user_vote': vote if action != 'removed' else None
        })
    except Exception as e:
        logger.error(f"Error in like_dislike: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# @require_POST
# @login_required
# def add_comment(request):
#     try:
#         data = json.loads(request.body)
#         content_type = ContentType.objects.get(model=data['content_type'])
#         obj = content_type.get_object_for_this_type(pk=data['object_id'])
#
#         comment = Comment.objects.create(
#             user=request.user,
#             content_object=obj,
#             text=data['text']
#         )
#
#         # Отправка обновления через WebSocket
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             "updates",
#             {
#                 "type": "send_update",
#                 "data": {
#                     "content_type": data['content_type'],
#                     "object_id": data['object_id'],
#                     "comment": {
#                         'id': comment.id,
#                         'text': comment.text,
#                         'username': comment.user.username,
#                         'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
#                     },
#                     "action": "new_comment"
#                 }
#             }
#         )
#
#         return JsonResponse({
#             'success': True,
#             'comment': {
#                 'id': comment.id,
#                 'text': comment.text,
#                 'username': comment.user.username,
#                 'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
#             }
#         })
#     except Exception as e:
#         logger.error(f"Error in add_comment: {str(e)}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=400)