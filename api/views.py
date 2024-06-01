from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from django.db.models import Q


def get_linked_id(email, phone_number):
    contact = (
        Contact.objects.filter(Q(email=email) | Q(phone_number=phone_number))
        .order_by("created_at")
        .first()
    )
    return contact.id if contact.link_precedence == "primary" else contact.linked_id


def get_custom_response(contacts):
    primary_contact_id = contacts.order_by("created_at").first().id
    emails = set()
    phone_numbers = set()
    secondary_contact_ids = []
    for contact in contacts:
        emails.add(contact.email)
        phone_numbers.add(contact.phone_number)
        if contact.id != primary_contact_id:
            secondary_contact_ids.append(contact.id)
    data = {}
    data["contact"] = {}
    data["contact"]["primaryContatctId"] = primary_contact_id
    data["contact"]["emails"] = emails
    data["contact"]["phoneNumbers"] = phone_numbers
    data["contact"]["secondaryContactIds"] = secondary_contact_ids
    return Response(data, status=status.HTTP_200_OK)


def update_existing_contacts(email, phone_number):
    linked_id = get_linked_id(email, phone_number)
    secondary_contacts = Contact.objects.filter(
        Q(email=email) | Q(phone_number=phone_number)
    ).exclude(id=linked_id)
    for contact in secondary_contacts:
        contact.link_precedence = "secondary"
        contact.linked_id = linked_id
        contact.save()


def create_new_contact(email, phone_number, link_precedence, linked_id):
    new_contact = Contact.objects.create(
        email=email,
        phone_number=phone_number,
        link_precedence=link_precedence,
        linked_id=linked_id,
    )
    new_contact.save()


def create_new_contact(email, phone_number, link_precedence):
    create_new_contact(email, phone_number, link_precedence, None)


@api_view(["POST"])
def identify(request):
    email = request.data["email"]
    phone_number = request.data["phoneNumber"]
    link_precedence = "primary"
    if not Contact.objects.filter(
        Q(email=email) | Q(phone_number=phone_number)
    ).exists():
        create_new_contact(email, phone_number, link_precedence)
        return get_custom_response(
            Contact.objects.filter(email=email, phone_number=phone_number)
        )

    same_email_phone_contacts = Contact.objects.filter(
        email=email, phone_number=phone_number
    )
    same_email_different_phone_contacts = Contact.objects.exclude(
        phone_number=phone_number
    ).filter(email=email)
    same_phone_different_email_contacts = Contact.objects.exclude(email=email).filter(
        phone_number=phone_number
    )

    if len(same_email_phone_contacts):
        return get_custom_response(
            same_email_phone_contacts
            | same_email_different_phone_contacts
            | same_phone_different_email_contacts
        )

    linked_id = get_linked_id(email, phone_number)
    if len(same_email_different_phone_contacts) and len(
        same_phone_different_email_contacts
    ):
        update_existing_contacts(email, phone_number)
    elif phone_number is not None and email is not None:
        link_precedence = "secondary"
        create_new_contact(email, phone_number, link_precedence, linked_id)

    return get_custom_response(
        Contact.objects.filter(
            Q(email=email)
            | Q(phone_number=phone_number)
            | Q(linked_id=linked_id)
            | Q(id=linked_id)
        )
    )
