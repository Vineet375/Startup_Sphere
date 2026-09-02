from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Startup, Activity, Notification

@receiver(pre_save, sender=Startup)
def capture_startup_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Startup.objects.get(pk=instance.pk)
            instance._old_mentor = old_instance.mentor
            instance._old_incubation_status = old_instance.incubation_status
        except Startup.DoesNotExist:
            instance._old_mentor = None
            instance._old_incubation_status = None
    else:
        instance._old_mentor = None
        instance._old_incubation_status = None

@receiver(post_save, sender=Startup)
def log_startup_changes(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        # Check for mentor change
        if hasattr(instance, '_old_mentor'):
            old_mentor = instance._old_mentor
            new_mentor = instance.mentor
            startup_url = reverse('incubator:startup_detail_id', args=[instance.id])
            if old_mentor != new_mentor:
                if old_mentor is None and new_mentor is not None:
                    Activity.objects.create(
                        startup=instance,
                        user=new_mentor,
                        activity_type='mentor_assigned',
                        description=f"Mentor {new_mentor.get_full_name() or new_mentor.username} was assigned."
                    )
                    Notification.objects.create(
                        recipient=instance.founder,
                        actor=new_mentor,
                        startup=instance,
                        title="Mentor Assigned",
                        message=f"A mentor ({new_mentor.get_full_name() or new_mentor.username}) has been assigned to your startup.",
                        notification_type='mentor_assigned',
                        link_url=startup_url
                    )
                    Notification.objects.create(
                        recipient=new_mentor,
                        actor=None,
                        startup=instance,
                        title="New Startup Assigned",
                        message=f"You have been assigned to mentor {instance.name}.",
                        notification_type='mentor_assigned',
                        link_url=startup_url
                    )
                elif old_mentor is not None and new_mentor is None:
                    Activity.objects.create(
                        startup=instance,
                        user=old_mentor,
                        activity_type='mentor_removed',
                        description=f"Mentor {old_mentor.get_full_name() or old_mentor.username} was removed."
                    )
                    # No notification for mentor removal as requested.
                elif old_mentor is not None and new_mentor is not None:
                    Activity.objects.create(
                        startup=instance,
                        user=new_mentor,
                        activity_type='mentor_changed',
                        description=f"Mentor was changed from {old_mentor.get_full_name() or old_mentor.username} to {new_mentor.get_full_name() or new_mentor.username}."
                    )
                    Notification.objects.create(
                        recipient=instance.founder,
                        actor=new_mentor,
                        startup=instance,
                        title="Mentor Changed",
                        message=f"Your startup's mentor has been changed to {new_mentor.get_full_name() or new_mentor.username}.",
                        notification_type='mentor_changed',
                        link_url=startup_url
                    )
                    Notification.objects.create(
                        recipient=new_mentor,
                        actor=None,
                        startup=instance,
                        title="New Startup Assigned",
                        message=f"You have been assigned to mentor {instance.name}, replacing a previous mentor.",
                        notification_type='mentor_changed',
                        link_url=startup_url
                    )

        # Check for incubation status change
        if hasattr(instance, '_old_incubation_status'):
            old_status = instance._old_incubation_status
            new_status = instance.incubation_status
            if old_status != new_status:
                old_display = dict(Startup.INCUBATION_CHOICES).get(old_status, old_status)
                new_display = dict(Startup.INCUBATION_CHOICES).get(new_status, new_status)
                Activity.objects.create(
                    startup=instance,
                    user=None,
                    activity_type='status_changed',
                    description=f"Startup status changed from {old_display} to {new_display}."
                )
                startup_url = reverse('incubator:startup_detail_id', args=[instance.id])
                Notification.objects.create(
                    recipient=instance.founder,
                    actor=None,
                    startup=instance,
                    title="Startup Status Changed",
                    message=f"Your startup status changed from {old_display} to {new_display}.",
                    notification_type='startup_status_changed',
                    link_url=startup_url
                )
