#!/bin/bash
python manage.py syncdb --settings helpdesk_proj.settings.local
python manage.py runserver --settings helpdesk_proj.settings.local
