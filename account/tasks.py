from celery import shared_task

from account.views import AccountViews

task = AccountViews()

@shared_task
def automate_all_account_process_scheduler():
    # use the views function to automate the process

    task.automate_all_account_process()


@shared_task
def automate_update_process_day():
    # use the views function to automate the process

    task.update_process_day()


@shared_task
def automate_all_account_update_bio():
    # use the views function to automate the process

    task.automate_bio_strategy()
