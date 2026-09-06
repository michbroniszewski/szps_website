from django.shortcuts import render

from .models import BoardMember


def member_list(request):
    members = BoardMember.objects.filter(is_active=True)
    return render(
        request,
        "board/list.html",
        {"members": members, "active_nav": "board"},
    )
