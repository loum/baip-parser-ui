"""BAIP Parser UI views abstraction.
"""
import flask
import werkzeug
import os
import urlparse

import baip_parser_ui
import baip_parser
from baip_parser_ui.utils import allowed_file
from logga.log import log
from filer.files import (get_directory_files_list,
                         remove_files)


@baip_parser_ui.app.route('/parser/health')
def health():
    """Quick health check response

    """
    return flask.render_template('health.html')


@baip_parser_ui.app.route('/parser/dashboard')
@baip_parser_ui.app.route('/parser/dashboard/<path:path>')
def dashboard(path='.'):
    """Parser dashboard.

    """
    kwargs = {'path': path,
              'template': 'dashboard/layout.html',
              'endpoint': '.dashboard'}

    return baip_parser_ui.staging_index.render_autoindex(**kwargs)


@baip_parser_ui.app.route('/parser/upload')
@baip_parser_ui.app.route('/parser/upload/<path:path>')
def upload(path='.'):
    """Parser upload.

    """
    extensions = baip_parser_ui.app.config['ALLOWED_EXTENSIONS']
    extensions_formatted = ', '.join(['*.%s' % ext for ext in extensions])
    accept_formatted = ','.join(['.%s' % ext for ext in extensions])
    kwargs = {
        'path': path,
        'template': 'dashboard/upload.html',
        'template_context': {
            'extensions': extensions_formatted,
            'accept': accept_formatted,
            'download_icon': '/icons/page_white_put.png',
            'delete_icon': '/icons/delete.png',
        },
        'endpoint': '.upload'
    }

    return baip_parser_ui.staging_index.render_autoindex(**kwargs)


@baip_parser_ui.app.route('/parser/parse', methods=['GET', 'POST'])
@baip_parser_ui.app.route('/parser/parse/<path:path>')
def parse(path='.'):
    """Parser parse.

    """
    status = False

    if flask.request.method == 'POST':
        in_dir = baip_parser_ui.app.config['STAGING_DIR']
        log.debug('Parsing files: %s' % get_directory_files_list(in_dir))

        ready_dir = baip_parser_ui.app.config['READY_DIR']
        for html_file in get_directory_files_list(in_dir):
            target_file = os.path.join(ready_dir,
                                       os.path.basename(html_file))

            parser = baip_parser.Parser()

            if status:
                remove_files(html_file)
            else:
                break

    enabled = False
    kwargs = {
        'path': path,
        'template': 'dashboard/parse.html',
        'template_context': {
            'enabled': enabled,
            'status': status,
        },
        'endpoint': '.parse',
    }

    return baip_parser_ui.staging_index.render_autoindex(**kwargs)


@baip_parser_ui.app.route('/parser/upload_file', methods=['GET', 'POST'])
def upload_file():
    if flask.request.method == 'POST':
        file_storage = flask.request.files['file']
        source_file = None

        if file_storage:
            source_file = file_storage.filename
            log_msg = 'File "%s" ' % source_file
            log.info('%s has been selected for upload' % log_msg)

            extensions = baip_parser_ui.app.config['ALLOWED_EXTENSIONS']
            if allowed_file(source_file, extensions):
                filename = werkzeug.secure_filename(source_file)
                target = os.path.join(baip_parser_ui.app.config['UPLOAD_DIR'],
                                      filename)
                file_storage.save(target)
                log.info('%s uploaded to "%s"' % (log_msg, target))

    return flask.redirect(flask.url_for('upload'))


@baip_parser_ui.app.route('/parser/download')
@baip_parser_ui.app.route('/parser/download/<path:path>')
def download(path='.'):
    """Parser download.

    """
    kwargs = {
        'path': path,
        'template': 'dashboard/download.html',
        'template_context': {
            'download_icon': '/icons/page_white_put.png',
            'delete_icon': '/icons/delete.png',
        },
        'endpoint': '.download',
    }

    return baip_parser_ui.ready_index.render_autoindex(**kwargs)


@baip_parser_ui.app.route('/parser/_extensions')
def _extensions():
    file_to_upload = flask.request.args.get('file_to_upload')

    ext_status = False
    extensions = baip_parser_ui.app.config['ALLOWED_EXTENSIONS']
    if allowed_file(file_to_upload, extensions):
        ext_status = True

    return flask.jsonify(extension_ok=ext_status)


@baip_parser_ui.app.route('/parser/download_file/<filename>')
def download_file(filename):
    download_path = os.path.join(baip_parser_ui.app.config['READY_DIR'],
                                 filename)
    log.info('Attempting file download: "%s"' % download_path)

    return flask.send_from_directory(baip_parser_ui.app.config['READY_DIR'],
                                     filename,
                                     as_attachment=True)


@baip_parser_ui.app.route('/parser/delete_file/<filename>')
def delete_file(filename):
    """Delete a Parser staged or ready file from the server.

    Uses the request referrer value to determine which page initiates
    the request.  The deletion will occur within context of the referring
    page.  For example, delete request on the Uploads page will remove
    a file from the staging directory.

    **Args:**
        *filename*: name of the file to delete

    """
    referrer = flask.request.referrer
    log.debug('File deletion referrer: "%s"' % referrer)

    parsed_referrer_url = urlparse.urlparse(referrer)
    log.debug('File deletion referrer path: "%s"' %
              parsed_referrer_url.path)

    delete_path = baip_parser_ui.app.config['UPLOAD_DIR']
    route = 'upload'
    if parsed_referrer_url.path == '/parser/download':
        delete_path = baip_parser_ui.app.config['READY_DIR']
        route = 'download'

    delete_path = os.path.join(delete_path, filename)
    log.info('Attempting file delete: "%s"' % delete_path)
    remove_files(delete_path)

    return flask.redirect(flask.url_for(route))
