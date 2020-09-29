import sublime
import sublime_plugin

import html
import re
from base64 import b64decode
from datetime import timezone
from email.utils import parsedate_to_datetime


class EmailViewListener(sublime_plugin.ViewEventListener):

    SYNTAX = 'email.sublime-syntax'

    @classmethod
    def is_applicable(cls, settings):
        try:
            return (settings and
                    settings.get('syntax', '').lower().endswith(cls.SYNTAX))
        except Exception as e:
            return False

    def _pt2rgn_by_scope(self, point, scope):
        return next(
            r for r in self.view.find_by_selector(scope)
            if r.contains(point))

    def hover_base64(self, point):
        is_image = self.view.match_selector(point, 'meta.block.base64.image')

        expression_region = self._pt2rgn_by_scope(point, 'meta.block.base64')
        base64_text = self.view.substr(expression_region)

        if is_image:
            hover_text = '<img src="data:image/jpeg;base64, {}" />'.format(
                base64_text)
            # TODO: Add link to export image.
        else:
            try:
                hover_text = b64decode(str.encode(base64_text)).decode()
                hover_lines = html.escape(hover_text).split('\n')[:50]
                hover_text = '\n'.join(self.format_hover_line(line)
                                       for line in hover_lines)
                # TODO: Add link to decode whole block in new `view`.
            except Exception as e:
                hover_text = 'Could not decode Base 64 to text'
        return '''
            <div id="render-base64">
                {}
            </div>
        '''.format(hover_text)

    def hover_datetime(self, point):
        expression_region = self._pt2rgn_by_scope(
            point, 'constant.numeric.date-time')
        date_str = re.sub(r'\s=?\s*', ' ', self.view.substr(expression_region))
        try:
            date = parsedate_to_datetime(date_str)
        except Exception as e:
            return 'Could not parse date'
        return '''
            <b style="color: var(--bluish);">Local Time</b>
            <div>{local:%c}</div>
            <div>{local}</div>
            <b style="color: var(--bluish);">UTC Time</b>
            <div>{utc:%c}</div>
            <div>{utc}</div>
        '''.format(
            local=date.astimezone(),
            utc=date.astimezone(timezone.utc),
        )

    def format_hover_line(self, text):
        text = text.replace('  ', ' &nbsp;').replace('\t', '&nbsp;' * 4)
        return '<div>{}&nbsp;</div>'.format(text)

    def on_hover(self, point, hover_zone):

        hover_scopes = {
            'meta.block.base64': self.hover_base64,
            'constant.numeric.date-time': self.hover_datetime,
        }

        if ((hover_zone != sublime.HOVER_TEXT or not self.view.match_selector(
                point, ','.join(k for k in hover_scopes)))):
            return

        # Run the function for the first matching scope
        for scope, method in hover_scopes.items():
            if self.view.match_selector(point, scope):
                hover_text = method(point)
                break

        html_text = '''
            <body>
                {}
            </body>
        '''.format(hover_text)

        self.view.show_popup(html_text, sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                             location=point,)
