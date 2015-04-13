from fabric.api import *
from fabric.contrib.console import confirm
import os

user='helpdesk'
app_name = 'helpdesk'
project_name = 'helpdesk_proj'
project_dir = "/srv/www/helpdesk.rufian.eu/"
miau_root = os.path.expanduser("~/django-miau/miau")

env.hosts = ['root@rufian.eu']

def update():
    local("rsync --delete -r -P %s %s:%s/env/lib/python2.7/site-packages/" % \
            (miau_root, env.host_string, project_dir))
    local("rsync -r -P %s %s:%s/" % \
            (project_name, env.host_string, project_dir))
    run("chown -R %s: %s/%s" % (user, project_dir, project_name))
    run("chmod -R g=,o= %s/%s" % (project_dir, project_name))
    with cd(project_dir + '/' + project_name):
        manage = "../env/bin/python manage.py "
        settings = "--settings=helpdesk_proj.settings.production"
        sudo("umask 077; %s syncdb %s" % (manage, settings), user=user)
        run("umask 022; %s collectstatic %s --noinput" % (manage, settings))

def restart():
    run("systemctl restart helpdeskweb")
    run("systemctl restart helpdeskmiau")

def deploy():
    update()
    restart()
