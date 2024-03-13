template_content = ('''
<!DOCTYPE html>
<html>
<head>
    <title>Hello, Mako!</title>
</head>
<body>
    <h1>Hello, ${name}!</h1>
</body>
</html>
''')

def render_template():
    from mako.template import Template
    template_obj = Template(template_content)
    data = {'name': 'World'}
    rendered_template = template_obj.render(**data)
    print(rendered_template)

if __name__ == '__main__':
    render_template()
