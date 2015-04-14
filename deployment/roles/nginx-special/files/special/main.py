from __future__ import division
from flask import Flask, request, abort, render_template, redirect
from werkzeug.exceptions import HTTPException
from datetime import datetime
import mimetypes
import os
import sys
import re

app = Flask(__name__)
app.config.from_object('config')

# Register {% strip %}
app.jinja_env.add_extension('jinja2htmlcompress.SelectiveHTMLCompress')

@app.context_processor
def inject_static_url():
    return dict(static_url=app.config['STATIC_URL'])

def get_document_root():
    if not app.debug:
        print(request.environ['HTTP_DOCUMENT_ROOT'])
        return request.environ['HTTP_DOCUMENT_ROOT']
    else:
        return '/'

re_filter = re.compile(r'^\.|.*~$')
def filter_file_name(file_name):
    return re_filter.match(file_name)

class EntryInfo(object):
    def __init__(self, path):
        self.name = os.path.basename(path).decode('UTF-8')

        stat = os.lstat(path)
        self.last_modified = datetime.fromtimestamp(stat.st_mtime)
        self.size = stat.st_size

        if os.path.isdir(path):
            self.type = 'Directory'
            self.encoding = None
            self.size = None
            self.dir = True
        else:
            self.type, self.encoding = mimetypes.guess_type(path)
            self.dir = False

    @property
    def size_text(self):
        if self.dir:
            return '-'
        else:
            return short_size(self.size)

    @property
    def type_text(self):
        return self.type or u'Unknown' + \
                (' (%s)' % self.encoding if self.encoding else '')

    def __lt__(self, other):
        if self.dir == other.dir:
            return self.name.lower() < other.name.lower()
        else:
            return self.dir

@app.template_filter('iso_date')
def iso_date(date):
    return date.isoformat(' ').rsplit('.')[0]

@app.template_filter('short_size')
def short_size(size):
    if size < 1024:
        return '%dB' % (size)
    elif size < 1024 ** 2:
        return '%.1fK' % (size / 1024)
    elif size < 1024 ** 3:
        return '%.1fM' % (size / 1024 ** 2)
    elif size < 1024 ** 4:
        return '%.1fG' % (size / 1024 ** 3)

@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(502)
@app.route("/error/<int:code>/")
def error_handler(error=None, code=None):
    if error is not None:
        if isinstance(error, HTTPException):
            code = error.code
        else: # Other Python exception
            code = 500

    try:
        status_text = {
            403: 'Blocked by Godzilla',
            404: 'Under Godzilla Attack',
            500: 'Godzilla Server Seizure',
            502: 'Bad Godzilla',
            503: 'Godzilla Unavailable',
        }[code]
    except KeyError:
        abort(404)

    template = request.args.get('template') or code

    return render_template('%s.html' % template, error_code=code,
                           status_text=status_text), \
                           '%s %s' % (code, status_text)

if not app.debug:
    error_handler = app.errorhandler(500)(error_handler)

@app.route("/dirlist/<path:requested_path>")
@app.route("/dirlist/", defaults={"requested_path":"/"})
def dirlist(requested_path):
    path = os.path.normpath(requested_path) #the requested file or directory name
    dir_name = os.path.basename(path)
    # Make relative (i.e. '/anime/madoka' -> 'anime/madoka') in order to be joined
    rel_path = re.sub(r'^/+', '', path)
    # The requested path on the system
    system_path = os.path.normpath(os.path.join(get_document_root(), rel_path))

    # If path is a directory, assert URL ends in slash
    if not requested_path.endswith('/') and os.path.isdir(system_path):
        return redirect(request.path + '/')

    # Path to show in title
    if path == '/':
        fancy_path = '/'
    else:
        fancy_path = '/%s/' % path

    try:
        file_names = os.listdir(system_path)
    except OSError as e:
        if e.errno == 2: # No such file or directory
            abort(404) # Not found
        elif e.errno == 13: # Permission denied
            abort(403) # Permission denied
        else:
            abort(500) # Internal server error

    entries = sorted(
            EntryInfo(os.path.join(system_path, file_name))
            for file_name in file_names
            if not filter_file_name(file_name))

    return render_template('dirlist.html',
            dir_name=dir_name,
            path=fancy_path,
            entries=entries)

if __name__ == "__main__":
    app.run()
