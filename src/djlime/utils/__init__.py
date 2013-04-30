"""
    djlime.utils
    ~~~~~~~~~~~~~~

    Utilities.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""

import os
import uuid


def get_file_path(obj, filename):
    if hasattr(obj, 'upload_dir'):
        extension = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), extension)
        return os.path.join(obj.upload_dir, filename)
    else:
        raise AttributeError("%s does not have 'upload_dir' attribute" % obj.__class__.__name__)
