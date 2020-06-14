import sublime
import sublime_plugin

from base64 import b64decode
import html


class EmailViewListener(sublime_plugin.ViewEventListener):

    SYNTAX = 'email.sublime-syntax'

    @classmethod
    def is_applicable(cls, settings):
        try:
            return (settings and
                    settings.get('syntax', '').lower().endswith(cls.SYNTAX))
        except Exception as e:
            return False

    def format_hover_line(self, text):
        text = text.replace('  ', ' &nbsp;').replace('\t', '&nbsp;' * 4)
        return '<div>{}&nbsp;</div>'.format(text)

    def on_hover(self, point, hover_zone):
        if ((hover_zone != sublime.HOVER_TEXT or not
             self.view.match_selector(point, 'meta.block.base64'))):
            return

        is_image = self.view.match_selector(point, 'meta.block.base64.image')

        expression_region = next(
            r for r in self.view.find_by_selector('meta.block.base64')
            if r.contains(point))

        base64_text = self.view.substr(expression_region)

        if is_image:
            hover_text = '<img src="data:image/jpeg;base64, {}" />'.format(
                base64_text)
        else:
            try:
                hover_text = b64decode(str.encode(base64_text)).decode()
                hover_lines = html.escape(hover_text).split('\n')[:50]
                hover_text = '\n'.join(self.format_hover_line(line)
                                       for line in hover_lines)
                # TODO: Add link to decode whole block in new `view`.
            except Exception as e:
                hover_text = 'Could not decode Base 64 to text'

        html_text = '''
            <body style="width: 500px;">
                <div id="render-base64">
                    {}
                </div>
            </body>
        '''.format(hover_text)

        self.view.show_popup(html_text, sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                             location=point,)
