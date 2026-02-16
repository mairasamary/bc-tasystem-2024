from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import TAEvaluation
from .forms import TAEvaluationForm

User = get_user_model()


def _professor_required(view_func):
    """Decorator that requires professor or superuser."""
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")
        if not (request.user.is_professor or request.user.is_superuser):
            messages.error(request, "Only professors can access TA evaluations.")
            return redirect("dashboard_v2")
        return view_func(request, *args, **kwargs)
    return wrapped


@login_required
@_professor_required
def evaluation_list(request):
    q = request.GET.get("q", "").strip()
    evaluations = TAEvaluation.objects.filter(reviewer=request.user).select_related(
        "ta", "course"
    )

    if q:
        all_for_ta = TAEvaluation.objects.filter(
            Q(ta__first_name__icontains=q) | Q(ta__last_name__icontains=q)
        ).select_related("ta", "course", "reviewer")
        context = {
            "evaluations": evaluations,
            "search_results": all_for_ta,
            "search_query": q,
        }
    else:
        context = {
            "evaluations": evaluations,
            "search_results": None,
            "search_query": "",
        }

    return render(request, "evaluations/evaluation_list.html", context)


@login_required
@_professor_required
def evaluation_create(request):
    form = TAEvaluationForm(professor=request.user)
    ta_id = request.GET.get("ta_id")
    course_id = request.GET.get("course_id")

    if request.method == "POST":
        form = TAEvaluationForm(request.POST, professor=request.user)
        if form.is_valid():
            existing = TAEvaluation.objects.filter(
                reviewer=request.user,
                ta=form.cleaned_data["ta"],
                course=form.cleaned_data["course"],
            ).first()
            if existing:
                messages.info(
                    request,
                    "You already evaluated this TA for this course. Redirecting to edit.",
                )
                return redirect("evaluations:edit", pk=existing.pk)
            eval_obj = form.save(commit=False)
            eval_obj.reviewer = request.user
            eval_obj.save()
            messages.success(request, "Evaluation saved successfully.")
            return redirect("evaluations:list")
    else:
        if ta_id and course_id:
            form.initial = {"ta": ta_id, "course": course_id}

    has_tas = form.fields["ta"].queryset.exists() if "ta" in form.fields else False
    return render(
        request,
        "evaluations/evaluation_form.html",
        {"form": form, "is_edit": False, "has_tas": has_tas},
    )


@login_required
@_professor_required
def evaluation_edit(request, pk):
    evaluation = get_object_or_404(TAEvaluation, pk=pk)
    if evaluation.reviewer != request.user:
        messages.error(request, "You can only edit your own evaluations.")
        return redirect("evaluations:list")

    if request.method == "POST":
        form = TAEvaluationForm(request.POST, instance=evaluation, professor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Evaluation updated successfully.")
            return redirect("evaluations:list")
    else:
        form = TAEvaluationForm(
            instance=evaluation, professor=request.user, readonly_ta_course=True
        )

    return render(
        request,
        "evaluations/evaluation_form.html",
        {"form": form, "evaluation": evaluation, "is_edit": True, "has_tas": True},
    )


@login_required
@_professor_required
def evaluation_delete(request, pk):
    evaluation = get_object_or_404(TAEvaluation, pk=pk)
    if evaluation.reviewer != request.user:
        messages.error(request, "You can only delete your own evaluations.")
        return redirect("evaluations:list")
    if request.method == "POST":
        evaluation.delete()
        messages.success(request, "Evaluation deleted.")
        return redirect("evaluations:list")
    return redirect("evaluations:list")
