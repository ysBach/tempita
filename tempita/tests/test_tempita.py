import pytest
from tempita import Template, sub, TemplateError, HTMLTemplate, sub_html, html, looper


def test_normal():
    assert sub('Hi {{name}}', name='Ian') == "Hi Ian"
    assert Template('Hi {{repr(name)}}').substitute(name='Ian') == "Hi 'Ian'"
    with pytest.raises(TypeError) as excinfo:
        Template('Hi {{name+1}}').substitute(name='Ian')
    assert sub('Hi ${name}', name='Ian', delimeters=('${', '}')) == "Hi Ian"
    assert Template('Hi $[[repr(name)]]', delimeters=('$[[', ']]')).substitute(name='Ian') == "Hi 'Ian'"
    assert sub('Hi {{name|repr}}', name='Ian') == "Hi 'Ian'"
    assert sub('Hi {{name}}', name=None) == "Hi "


def test_if_elif_else():
    t = Template('{{if x}}{{y}}{{else}}{{z}}{{endif}}')
    assert t.substitute(x=1, y=2, z=3) == "2"
    assert t.substitute(x=0, y=2, z=3) == "3"
    t = Template('{{if x > 0}}positive{{elif x < 0}}negative{{else}}zero{{endif}}')
    assert (t.substitute(x=1), t.substitute(x=-10), t.substitute(x=0)) == ("positive", "negative", "zero")


def test_for_loop():
    t = Template('{{for i in x}}i={{i}}\n{{endfor}}')
    assert t.substitute(x=range(3)) == 'i=0\ni=1\ni=2\n'
    t = Template('{{for a, b in sorted(z.items()):}}{{a}}={{b}},{{endfor}}')
    assert t.substitute(z={1: 2, 3: 4}) == '1=2,3=4,'
    t = Template('{{for i in x}}{{if not i}}{{break}}{{endif}}{{i}} {{endfor}}')
    assert t.substitute(x=[1, 2, 0, 3, 4]) == '1 2 '
    t = Template('{{for i in x}}{{if not i}}{{continue}}{{endif}}{{i}} {{endfor}}')
    assert t.substitute(x=[1, 2, 0, 3, 0, 4]) == '1 2 3 4 '


def test_python_blocks():
    assert sub('{{py:\nx=1\n}}{{x}}') == '1'


def test_syntax_errors():
    with pytest.raises(TemplateError) as excinfo:
        t = Template('{{if x}}', name='foo.html')
    with pytest.raises(TemplateError) as excinfo:
        t = Template('{{for x}}', name='foo2.html')


def test_html():
    assert sub_html('hi {{name}}', name='<foo>') == 'hi &lt;foo&gt;'
    assert sub_html('hi {{name}}', name=html('<foo>')) == 'hi <foo>'
    assert sub_html('hi {{name|html}}', name='<foo>') == 'hi <foo>'
    t = HTMLTemplate('<a href="article?id={{id|url}}" {{attr(class_=class_)}}>')
    assert t.substitute(id=1, class_='foo') == '<a href="article?id=1" class="foo">'
    assert t.substitute(id='with space', class_=None) == '<a href="article?id=with%20space" >'


def test_looper():
    seq = ['apple', 'asparagus', 'Banana', 'orange']
    out = []
    for loop, item in looper(seq):
        if item == 'apple':
            assert loop.first
        elif item == 'orange':
            assert loop.last
        if loop.first_group(lambda i: i[0].upper()):
            out.append('%s:' % item[0].upper())
        out.append((loop.number, item))
    assert out == [
        'A:',
        (1, 'apple'),
        (2, 'asparagus'),
        'B:',
        (3, 'Banana'),
        'O:',
        (4, 'orange'),
    ]


def test_strip():
    assert sub('{{if 1}}\n{{x}}\n{{endif}}\n', x=0) == '0\n'
    assert sub('{{if 1}}x={{x}}\n{{endif}}\n', x=1) == 'x=1\n'
    assert sub('{{if 1}}\nx={{x}}\n{{endif}}\n', x=1) == 'x=1\n'
    assert sub('  {{if 1}}  \nx={{x}}\n  {{endif}}  \n', x=1) == 'x=1\n'


def test_default_value():
    assert sub('{{default x=1}}{{x}}', x=2) == '2'
    assert sub('{{default x=1}}{{x}}') == '1'
    # The normal case:
    with pytest.raises(NameError) as excinfo:
        sub('{{x}}')
    assert "'x' is not defined" in str(excinfo.value)


def test_comments():
    assert sub('Test=x{{#whatever}}') == 'Test=x'


def test_get_template():
    global super_test
    def get_template(name, from_template):
        return globals()[name]

    tmpl = Template(
        '{{inherit "super_"+master}}\nHi there!\n{{def block}}some text{{enddef}}',
        get_template=get_template
    )
    super_test = Template(
        'This is the parent {{master}}. The block: {{self.block}}\nThen the body: {{self.body}}'
    )
    assert tmpl.substitute(master='test').strip() == "This is the parent test. The block: some text\nThen the body: Hi there!"

    tmpl2 = Template(
        "{{def block(arg='hi_'+master):}}hey {{master}}: {{arg}}{{enddef}}",
        get_template=get_template,
        default_inherit='super_test'
    )
    assert tmpl2.substitute(master='test2').strip() == """This is the parent test2. The block: hey test2: hi_test2\nThen the body:"""

    super_test = Template("The block: {{self.block('blah')}}")
    assert tmpl2.substitute(master='test2').strip() == """The block: hey test2: blah"""
    super_test = Template("Something: {{self.get.something('hi')}}")
    assert tmpl2.substitute(master='test2').strip() == """Something:"""


def test_whitespace():
    tmpl = Template('''\
    {{for i, item in enumerate(['a', 'b'])}}
        {{if i % 2 == 0}}
      <div class='even'>
        {{else}}
      <div class='odd'>
        {{endif}}
        {{item}}
      </div>
    {{endfor}}''')
    assert tmpl.substitute() == '''\
      <div class='even'>
        a
      </div>
      <div class='odd'>
        b
      </div>
'''
"""
Normal templating
=================

The templating language is fairly simple, just ``{{stuff}}``.  For
example::

    >>> from tempita import Template, sub
    >>> sub('Hi {{name}}', name='Ian')
    'Hi Ian'
    >>> Template('Hi {{repr(name)}}').substitute(name='Ian')
    "Hi 'Ian'"
    >>> Template('Hi {{name+1}}').substitute(name='Ian') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    TypeError: cannot concatenate 'str' and 'int' objects at line 1 column 6

You can also specifiy delimeters::

    >>> sub('Hi ${name}', name='Ian', delimeters=('${', '}'))
    'Hi Ian'
    >>> Template('Hi $[[repr(name)]]', delimeters=('$[[', ']]')).substitute(name='Ian')
    "Hi 'Ian'"

It also has Django-style piping::

    >>> sub('Hi {{name|repr}}', name='Ian')
    "Hi 'Ian'"

Note that None shows up as an empty string::

    >>> sub('Hi {{name}}', name=None)
    'Hi '

And if/elif/else::

    >>> t = Template('{{if x}}{{y}}{{else}}{{z}}{{endif}}')
    >>> t.substitute(x=1, y=2, z=3)
    '2'
    >>> t.substitute(x=0, y=2, z=3)
    '3'
    >>> t = Template('{{if x > 0}}positive{{elif x < 0}}negative{{else}}zero{{endif}}')
    >>> t.substitute(x=1), t.substitute(x=-10), t.substitute(x=0)
    ('positive', 'negative', 'zero')

Plus a for loop::

    >>> t = Template('{{for i in x}}i={{i}}\n{{endfor}}')
    >>> t.substitute(x=range(3))
    'i=0\ni=1\ni=2\n'
    >>> t = Template('{{for a, b in sorted(z.items()):}}{{a}}={{b}},{{endfor}}')
    >>> t.substitute(z={1: 2, 3: 4})
    '1=2,3=4,'
    >>> t = Template('{{for i in x}}{{if not i}}{{break}}'
    ...              '{{endif}}{{i}} {{endfor}}')
    >>> t.substitute(x=[1, 2, 0, 3, 4])
    '1 2 '
    >>> t = Template('{{for i in x}}{{if not i}}{{continue}}'
    ...              '{{endif}}{{i}} {{endfor}}')
    >>> t.substitute(x=[1, 2, 0, 3, 0, 4])
    '1 2 3 4 '

Also Python blocks::

    >>> sub('{{py:\nx=1\n}}{{x}}')
    '1'

And some syntax errors::

    >>> t = Template('{{if x}}', name='foo.html') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    TemplateError: No {{endif}} at line 1 column 3 in foo.html
    >>> t = Template('{{for x}}', name='foo2.html')
    Traceback (most recent call last):
        ...
    TemplateError: Bad for (no "in") in 'x' at line 1 column 3 in foo2.html

There's also an HTMLTemplate that uses HTMLisms::

    >>> from tempita import HTMLTemplate, sub_html, html
    >>> sub_html('hi {{name}}', name='<foo>')
    'hi &lt;foo&gt;'

But if you don't want quoting to happen you can do::

    >>> sub_html('hi {{name}}', name=html('<foo>'))
    'hi <foo>'
    >>> sub_html('hi {{name|html}}', name='<foo>')
    'hi <foo>'

Also a couple handy functions;:

    >>> t = HTMLTemplate('<a href="article?id={{id|url}}" {{attr(class_=class_)}}>')
    >>> t.substitute(id=1, class_='foo')
    '<a href="article?id=1" class="foo">'
    >>> t.substitute(id='with space', class_=None)
    '<a href="article?id=with%20space" >'

There's a handyish looper thing you can also use in your templates (or
in Python, but it's more useful in templates generally)::

    >>> from tempita import looper
    >>> seq = ['apple', 'asparagus', 'Banana', 'orange']
    >>> for loop, item in looper(seq):
    ...     if item == 'apple':
    ...         assert loop.first
    ...     elif item == 'orange':
    ...         assert loop.last
    ...     if loop.first_group(lambda i: i[0].upper()):
    ...         print('%s:' % item[0].upper())
    ...     print(loop.number, item)
    A:
    (1, 'apple')
    (2, 'asparagus')
    B:
    (3, 'Banana')
    O:
    (4, 'orange')

It will also strip out empty lines, when there is a line that only
contains a directive/statement (if/for, etc)::

    >>> sub('{{if 1}}\n{{x}}\n{{endif}}\n', x=0)
    '0\n'
    >>> sub('{{if 1}}x={{x}}\n{{endif}}\n', x=1)
    'x=1\n'
    >>> sub('{{if 1}}\nx={{x}}\n{{endif}}\n', x=1)
    'x=1\n'
    >>> sub('  {{if 1}}  \nx={{x}}\n  {{endif}}  \n', x=1)
    'x=1\n'

There is a special directive that will create a default value
for a variable, if no value is given::

    >>> sub('{{default x=1}}{{x}}', x=2)
    '2'
    >>> sub('{{default x=1}}{{x}}')
    '1'
    >>> # The normal case:
    >>> sub('{{x}}')
    Traceback (most recent call last):
        ...
    NameError: global name 'x' is not defined at line 1 column 3

And comments work::

    >>> sub('Test=x{{#whatever}}')
    'Test=x'

Inheritance
===========

You can have inherited templates; you have to pass in some kind of
get_template function, for example::

    >>> def get_template(name, from_template):
    ...     return globals()[name]

Then we'll define a template that inherits::

    >>> tmpl = Template('''\
    ... {{inherit "super_"+master}}
    ... Hi there!
    ... {{def block}}some text{{enddef}}
    ... ''', get_template=get_template)
    >>> super_test = Template('''\
    ... This is the parent {{master}}. The block: {{self.block}}
    ... Then the body: {{self.body}}
    ... ''')
    >>> print(tmpl.substitute(master='test').strip())
    This is the parent test. The block: some text
    Then the body: Hi there!
    >>> tmpl2 = Template('''\
    ... {{def block(arg='hi_'+master):}}hey {{master}}: {{arg}}{{enddef}}
    ... ''', get_template=get_template, default_inherit='super_test')
    >>> print(tmpl2.substitute(master='test2').strip())
    This is the parent test2. The block: hey test2: hi_test2
    Then the body:
    >>> super_test = Template('''\
    ... The block: {{self.block('blah')}}
    ... ''')
    >>> print(tmpl2.substitute(master='test2').strip())
    The block: hey test2: blah
    >>> super_test = Template('''\
    ... Something: {{self.get.something('hi')}}
    ... ''')
    >>> print(tmpl2.substitute(master='test2').strip())
    Something:

Whitespace
==========

Whitespace is removed from templates when a directive is on a line by
itself.  For example::

    >>> #import sys; sys.debug = True
    >>> tmpl = Template('''\
    ... {{for i, item in enumerate(['a', 'b'])}}
    ...     {{if i % 2 == 0}}
    ...   <div class='even'>
    ...     {{else}}
    ...   <div class='odd'>
    ...     {{endif}}
    ...     {{item}}
    ...   </div>
    ... {{endfor}}''')
    >>> print(tmpl.substitute())
      <div class='even'>
        a
      </div>
      <div class='odd'>
        b
      </div>
    <BLANKLINE>
"""
