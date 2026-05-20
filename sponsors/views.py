from django.shortcuts import render
from .models import Sponsor


def sponsor_list(request):
    # Single query; group in Python to avoid one DB hit per tier
    all_sponsors = list(Sponsor.objects.filter(is_active=True))
    sponsors_by_tier = {}
    for tier_key, tier_label in Sponsor.TIER_CHOICES:
        group = [s for s in all_sponsors if s.tier == tier_key]
        if group:
            sponsors_by_tier[tier_label] = group
    return render(request, "sponsors/list.html", {"sponsors_by_tier": sponsors_by_tier})
