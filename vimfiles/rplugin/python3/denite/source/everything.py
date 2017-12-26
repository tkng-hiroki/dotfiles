from denite import util, process
from .base import Base
import os
import os.path
from denite.util import abspath

def _candidate(result, path):
    return {
        'word': result[3],
        'abbr': '{0}:{1}{2} {3}'.format(
            path,
            result[1],
            (':' + result[2] if result[2] != '0' else ''),
            result[3]),
        'action__path': result[0],
        'action__line': result[1],
        'action__col': result[2],
        'action__text': result[3],
    }

def follow_link(path):
    path = os.path.abspath(path)
    path_fragments = []
    current = ""
    while True:
        path, child = os.path.split(path)
        if child == '':
            current = path # /
            break
        path_fragments.insert(0, child)
    while path_fragments:
        current = follow_child(current, path_fragments[0])
        path_fragments = path_fragments[1:]
    return current

def follow_child(current, child):
    result = os.path.join(current, child)
    if not os.path.islink(result):
        return result
    link = os.readlink(result)
    if os.path.isabs(link):
        return link
    return os.path.abspath(os.path.join(current, link))

class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'everything'
        self.kind = 'file'

    def on_init(self, context):
        context['__proc'] = None
        context['__patterns'] = None
        context['is_interactive'] = True

        context['__arguments'] = ''
        for arg in context['args']:
            if arg == 'regex':
                context['__arguments'] += '-r '
            elif arg == 'case':
                context['__arguments'] += '-i '
            elif arg == 'word':
                context['__arguments'] += '-w '

        directory = context['args'][0] if len(
            context['args']) > 0 else context['path']
        context['__directory'] = follow_link(abspath(self.vim, directory))

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context):

        if context['event'] == 'interactive':
            self.on_close(context)

            if (not context['input']):
                return []

            context['__patterns'] = context['input']

        if context['__proc']:
            return self.__async_gather_candidates(context, context['async_timeout'])

        if not context['__patterns']:
            return []

        args = 'es.exe -n 100 '
        args += context['__arguments']
        args += context['__directory'] + ' '
        args += context['__patterns']

        self.print_message(context, args)

        context['__proc'] = process.Process(args, context, context['path'])
        return self.__async_gather_candidates(context, 0.5)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(errs)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []

        for line in outs:
            candidates.append({
                'word': line,
                'abbr': line + ('/' if os.path.isdir(line) else ''),
                'kind': ('directory' if os.path.isdir(line) else 'file'),
                'action__path': abspath(self.vim, line),
                })

        return candidates

