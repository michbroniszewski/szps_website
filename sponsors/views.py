from django.shortcuts import render
from .models import Sponsor


def sponsor_list(request):
    sponsors_by_tier = {}
    for tier_key, tier_label in Sponsor.TIER_CHOICES:
        qs = Sponsor.objects.filter(tier=tier_key, is_active=True)
        if qs.exists():
            sponsors_by_tier[tier_label] = qs
    return render(request, "sponsors/list.html", {"sponsors_by_tier": sponsors_by_tier})
