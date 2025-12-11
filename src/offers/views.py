from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from applications.models import Application
from .models import Offer
from django.urls import reverse
from django.contrib import messages
from django.conf import settings


class OfferCreateView(
    SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView
):
    model = Offer
    template_name = "offer_form.html"
    success_message = "Your offer has been submitted successfully!"
    fields = []

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.get_object().student
        form.instance.course = self.get_object().course
        form.instance.application = self.get_object()

        self.get_object().accept()

        return super().form_valid(form)

    def get_object(self):
        return Application.objects.get(pk=self.kwargs.get("pk"))

    def test_func(self):
        if self.get_object().get_status() != "PENDING":
            return False
        return (
            self.get_object().course.professor == self.request.user
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.get_object()
        return context

    def get_success_url(self):
        application = self.get_object()
        student = application.student
        course = application.course
        offer = Offer.objects.get(application=application)
        url = reverse("offers:offer-detail", args=[offer.id])
        subject = f"TA Application Update For {student}"
        message = [
            f"Dear {student}",
            f"Congratulations! You have received an offer for {course}",
            f"Access the offer here: http://cscigpu03.bc.edu:8080{url}",
        ]
        if student.email:
            recipients = student.email
            send_html_email(subject, recipients, message)
        return reverse("offers:offer-list")


class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = "offers.html"
    context_object_name = "offers"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Offer.objects.all()
        elif self.request.user.is_student():
            return Offer.objects.filter(recipient=self.request.user)
        else:
            return Offer.objects.filter(course__professor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offers"] = self.get_queryset()
        if self.request.user.is_student():
            context["title"] = "My Offers"
        else:
            context["title"] = "Offers"
        return context


class OfferDeleteView(
    SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView
):
    model = Offer
    success_message = "Your offer has been deleted successfully!"
    template_name = "offer_confirm_delete.html"

    def form_valid(self, form):
        Offer.objects.get(pk=self.kwargs.get("pk")).application.reset()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("offers:offer-list")

    def test_func(self):
        offer = self.get_object()
        if offer.get_status() != "PENDING":
            return False
        return (
            self.get_object().sender == self.request.user
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OfferAcceptView(
    SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = Offer
    template_name = "offer_accept.html"
    success_message = "Your offer has been accepted successfully!"
    fields = []

    def form_valid(self, form):
        error = self.ensure_user_can_accept()
        if error:
            messages.error(self.request, error)
            return self.form_invalid(form)
        self.object.accept()
        return super().form_valid(form)

    def test_func(self):
        return (
            self.get_object().recipient == self.request.user
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.get_object().application
        return context

    def get_success_url(self):
        offer = self.get_object()
        course = offer.course
        url = reverse("courses:course-detail", args=[course.id])
        subject = f"TA Offer Update For {course.instructor_first_name} {course.instructor_last_name}"
        message = [
            f"Dear {course.instructor_first_name} {course.instructor_last_name}",
            f"The student has accepted your offer. You can view the status of {course} here: http://cscigpu03.bc.edu:8080{url}",
        ]
        if course.professor and course.professor.email:
            recipients = course.professor.email
            send_html_email(subject, recipients, message)
        return reverse("offers:offer-list")

    def ensure_user_can_accept(self):
        user = self.request.user
        course = self.get_object().course
        if user.is_ta():
            return "You are already a TA for a course"
        if course.current_tas.count() >= course.num_tas:
            return "This course already has the maximum number of TAs"


class OfferDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Offer
    template_name = "offer_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = self.get_object()
        return context

    def test_func(self):
        return (
            self.get_object().recipient == self.request.user
            or self.request.user.is_superuser
        )


class OfferRejectView(
    SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = Offer
    fields = []
    template_name = "offer_reject.html"
    success_message = "Your offer has been rejected successfully!"

    def form_valid(self, form):
        self.object.reject()
        return super().form_valid(form)

    def get_success_url(self):
        offer = self.get_object()
        course = offer.course
        url = reverse("courses:course-detail", args=[course.id])
        subject = f"TA Offer Update For {course.instructor_first_name} {course.instructor_last_name}"
        message = [
            f"Dear {course.instructor_first_name} {course.instructor_last_name}",
            f"The student has declined your offer. You can view the status of {course} here: http://cscigpu03.bc.edu:8080{url}",
        ]
        if course.professor and course.professor.email:
            recipients = course.professor.email
            send_html_email(subject, recipients, message)
        return reverse("offers:offer-list")

    def test_func(self):
        return (
            self.get_object().recipient == self.request.user
            or self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = self.get_object().application
        return context


def send_html_email(subject, recipients, message):
    """
    Send an HTML email for offer accept/reject notifications.
    Arguments:
        subject: Email subject.
        recipients: string or list of email addresses.
        message: List of message lines (rendered into template).
    """
    if settings.ENV != "prod":
        print("Email not sent in non-production environment")
        return

    if not recipients:
        return

    if isinstance(recipients, str):
        recipients = [recipients]

    try:
        from_email = "cscita@bc.edu"
        context = {"messages": message}
        html_content = render_to_string("email.html", context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        # Log the error but don't fail the request
        # In production, you might want to use Django's logging framework
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email to {recipients}: {str(e)}")
