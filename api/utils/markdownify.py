# This is a modified copy of markdownify.
##################################################################
# The original version of Markdownify is licensed as:
# The MIT License (MIT)

# Copyright 2012-2018 Matthew Tretter

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE. 
###################################################################
from bs4 import BeautifulSoup, NavigableString
import re
import six
import requests


convert_heading_re = re.compile(r'convert_h(\d+)')
line_beginning_re = re.compile(r'^', re.MULTILINE)
whitespace_re = re.compile(r'[\r\n\s\t ]+')
html_heading_re = re.compile(r'h[1-6]')


# Heading styles
ATX = 'atx'
ATX_CLOSED = 'atx_closed'
UNDERLINED = 'underlined'
SETEXT = UNDERLINED


def escape(text):
    if not text:
        return ''
    return text.replace('_', r'\_')


def chomp(text):
    """
    If the text in an inline tag like b, a, or em contains a leading or trailing
    space, strip the string and return a space as suffix of prefix, if needed.
    This function is used to prevent conversions like
        <b> foo</b> => ** foo**
    """
    prefix = ' ' if text and text[0] == ' ' else ''
    suffix = ' ' if text and text[-1] == ' ' else ''
    text = text.strip()
    return (prefix, suffix, text)


def _todict(obj):
    return dict((k, getattr(obj, k)) for k in dir(obj) if not k.startswith('_'))

def urlParser(url):
    if "https://clientless.wusys.net/proxy/" == url[0:35]:
        u = url[35:]
        u = u[u.find("/")+1:]
        pos = u.find("/")
        if u[:pos] == "https":
            return "https://"+u[pos+1:]
        elif u[:pos] == "http":
            return"http://"+u[pos+1:]
        else:
            print("WARNING:", "Url could not be parsed. Defaulting.:", url)
            return url
    else:
        return url

class MarkdownConverter(object):
    class DefaultOptions:
        strip = None
        convert = None
        autolinks = False # ADJUSTED: Autolinks disabled cause the parser cannot handle this
        heading_style = UNDERLINED
        bullets = '*+-'  # An iterable of bullet types.

    class Options(DefaultOptions):
        pass

    def __init__(self, **options):
        # Create an options dictionary. Use DefaultOptions as a base so that
        # it doesn't have to be extended.
        self.options = _todict(self.DefaultOptions)
        self.options.update(_todict(self.Options))
        self.options.update(options)
        if self.options['strip'] is not None and self.options['convert'] is not None:
            raise ValueError('You may specify either tags to strip or tags to'
                             ' convert, but not both.')

    def convert(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return self.process_tag(soup, convert_as_inline=False, children_only=True)

    def process_tag(self, node, convert_as_inline, children_only=False):
        text = ''
        # markdown headings can't include block elements (elements w/newlines)
        isHeading = html_heading_re.match(node.name) is not None
        convert_children_as_inline = convert_as_inline

        if not children_only and isHeading:
            convert_children_as_inline = True

        # Convert the children first
        for el in node.children:
            if isinstance(el, NavigableString):
                text += self.process_text(six.text_type(el))
            else:
                text += self.process_tag(el, convert_children_as_inline)

        if not children_only:
            convert_fn = getattr(self, 'convert_%s' % node.name, None)
            if convert_fn and self.should_convert_tag(node.name):
                text = convert_fn(node, text, convert_as_inline)

        return text

    def process_text(self, text):
        return escape(whitespace_re.sub(' ', text or ''))

    def __getattr__(self, attr):
        # Handle headings
        m = convert_heading_re.match(attr)
        if m:
            n = int(m.group(1))

            def convert_tag(el, text, convert_as_inline):
                return self.convert_hn(n, el, text, convert_as_inline)

            convert_tag.__name__ = 'convert_h%s' % n
            setattr(self, convert_tag.__name__, convert_tag)
            return convert_tag

        raise AttributeError(attr)

    def should_convert_tag(self, tag):
        tag = tag.lower()
        strip = self.options['strip']
        convert = self.options['convert']
        if strip is not None:
            return tag not in strip
        elif convert is not None:
            return tag in convert
        else:
            return True

    def indent(self, text, level):
        return line_beginning_re.sub('\t' * level, text) if text else ''

    def underline(self, text, pad_char):
        text = (text or '').rstrip()
        return '%s\n%s\n\n' % (text, pad_char * len(text)) if text else ''

    def convert_a(self, el, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        if convert_as_inline:
            return text
        href = urlParser(el.get('href'))
        title = el.get('title')
        if self.options['autolinks'] and text == href and not title:
            # Shortcut syntax
            return '<%s>' % href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '%s[%s](%s%s)%s' % (prefix, text, href, title_part, suffix) if href else text

    def convert_b(self, el, text, convert_as_inline):
        return self.convert_strong(el, text, convert_as_inline)

    def convert_blockquote(self, el, text, convert_as_inline):

        if convert_as_inline:
            return text

        return '\n' + line_beginning_re.sub('> ', text) if text else ''

    def convert_br(self, el, text, convert_as_inline):
        if convert_as_inline:
            return ""

        return '  \n'

    def convert_em(self, el, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        return '%s*%s*%s' % (prefix, text, suffix)

    def convert_hn(self, n, el, text, convert_as_inline):
        if convert_as_inline:
            return text

        style = self.options['heading_style']
        text = text.rstrip()
        if style == UNDERLINED and n <= 2:
            line = '=' if n == 1 else '-'
            return self.underline(text, line)
        hashes = '#' * n
        if style == ATX_CLOSED:
            return '%s %s %s\n\n' % (hashes, text, hashes)
        return '%s %s\n\n' % (hashes, text)

    def convert_i(self, el, text, convert_as_inline):
        return self.convert_em(el, text, convert_as_inline)

    def convert_list(self, el, text, convert_as_inline):

        # Converting a list to inline is undefined.
        # Ignoring convert_to_inline for list.

        nested = False
        while el:
            if el.name == 'li':
                nested = True
                break
            el = el.parent
        if nested:
            # remove trailing newline if nested
            return '\n' + self.indent(text, 1).rstrip()
        return '\n' + text + '\n'

    convert_ul = convert_list
    convert_ol = convert_list

    def convert_li(self, el, text, convert_as_inline):
        parent = el.parent
        if parent is not None and parent.name == 'ol':
            if parent.get("start"):
                start = int(parent.get("start"))
            else:
                start = 1
            bullet = '%s.' % (start + parent.index(el))
        else:
            depth = -1
            while el:
                if el.name == 'ul':
                    depth += 1
                el = el.parent
            bullets = self.options['bullets']
            bullet = bullets[depth % len(bullets)]
        return '%s %s\n' % (bullet, text or '')

    def convert_p(self, el, text, convert_as_inline):
        if convert_as_inline:
            return text
        # The following code will take up to 5 seconds...
        res = ""
        # Check if inline-link actually exists (returns 200)
        for t in re.split(r'( )', text):
            link = re.search(r'^(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))', t.replace('\_', '_'))
            if link:
                link_text = link.group(1).replace('_', '\_')
                # If a link ends with . or , or ; it's likely to be incorrect.
                if any(link.group(1).endswith(s) for s in [",",";",".",":"]):
                    # Test if that link is working
                    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0"}
                    try:
                        r = requests.get(link.group(1), timeout=(3, 5), headers=headers)
                        r.raise_for_status()
                        res += '[%s](%s)%s' % (urlParser(link_text), link.group(1), t[len(link_text):])
                    except requests.exceptions.RequestException:
                        # try again with one charecter less (could be a . or so at the end)
                        try:
                            r = requests.get(link.group(1)[:-1], timeout=(5, 10), headers=headers)
                            r.raise_for_status()
                            res += '[%s](%s)%s' % (urlParser(link_text[:-1]), link.group(1)[:-1], t[len(link_text)-1:])
                        except requests.exceptions.RequestException:
                            #res += t
                            # it did not work so do not convert the link cause it is not clickable
                            res += '[%s](%s)%s' % (urlParser(link_text), link.group(1), t[len(link_text):])
                            # it did not work, but just ignore that.
                else:
                    res += '[%s](%s)%s' % (urlParser(link_text), link.group(1), t[len(link_text):])
            else:
                res += t
        return '- %s\n' % res if text else '' #modified

    def convert_strong(self, el, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        return '%s**%s**%s' % (prefix, text, suffix)

    def convert_img(self, el, text, convert_as_inline):
        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        if convert_as_inline:
            return alt

        return '![%s](%s%s)' % (alt, src, title_part)


def markdownify(html, **options):
    return MarkdownConverter(**options).convert(html)