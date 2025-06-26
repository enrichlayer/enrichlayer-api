from proxycurl.config import (
    BASE_URL, PROXYCURL_API_KEY, TIMEOUT, MAX_RETRIES, MAX_BACKOFF_SECONDS
)
from proxycurl.gevent.base import ProxycurlBase
from proxycurl.models import (
    {%- for namespace in ns_data %}
    {%- for result_class in ns_data[namespace]['result_classes'] %}
    {{result_class}},
    {%- endfor %}
    {%- endfor %}
)


{%- macro generate_method(action, options) %}
    def {{action}}(
        self,
        {%- for param in options['params'] %}
        {{param}}: {{options['params'][param]['type']}}{% if options['params'][param]['required'] == False %} = {{options['params'][param]['default']}}{% endif %},
        {%- endfor %}
        {%- for body in options['body'] %}
        {{body}}: {{options['body'][body]['type']}}{% if options['body'][body]['default'] %} = '{{options['body'][body]['default']}}'{% endif %},
        {%- endfor %}
    ) -> {{options['result_class']}}:
        """{{options['title']}}
        {% if '\n' in options['docstring'] %}
        {{options['docstring']|indent(8, True)}}
        {% else %}
        {{options['docstring']}}
        {% endif %}

        {%- for param in options['params'] %}
        :param {{param}}: {{options['params'][param]['description']}}{% if options['params'][param]['default'] %}, defaults to '{{options['params'][param]['default']}}'{% endif %}
        :type {{param}}: {{options['params'][param]['type']}}
        {%- endfor %}
        {%- for param in options['body'] %}
        :param {{param}}: {{options['body'][param]['description']}}{% if options['body'][param]['default'] %}, defaults to '{{options['body'][param]['default']}}'{% endif %}
        :type {{param}}: {{options['body'][param]['type']}}
        {%- endfor %}
        :return: An object of :class:`proxycurl.models.{{options['result_class']}}` or **None** if there is an error.
        :rtype: :class:`proxycurl.models.{{options['result_class']}}`
        :raise ProxycurlException: Every error will raise a :class:`proxycurl.gevent.ProxycurlException`

        """
        params = {}
        {%- for param in options['params'] %}
        {%- if not options['params'][param]['required'] %}
        if {{ param }} is not None:
            params['{{param}}'] = {{ param }}
        {%- else %}
        params['{{param}}'] = {{ param }}
        {%- endif %}
        {%- endfor %}

        return self.linkedin.proxycurl.request(
            method='{{options['method']}}',
            url='{{options['endpoint']}}',
            params=params,
            data={
                {%- for body in options['body'] %}
                '{{body}}': {{body}},
                {%- endfor %}
            },
            result_class={{options['result_class']}}
        )
{%- endmacro %}
{%- for namespace in ns_data %}
{%- if namespace != 'common' %}
{%- for package in ns_data[namespace]['packages'] %}


class _{{namespace.title()}}{{package.title()}}:
    def __init__(self, {{namespace}}):
        self.{{namespace}} = {{namespace}}
    {%- for action in ns_data[namespace]['packages'][package] %}
{{generate_method(action, ns_data[namespace]['packages'][package][action])}}
    {%- endfor %}
{%- endfor %}
{%- endif %}
{%- endfor %}
{%- for namespace in ns_data %}
{%- if namespace != 'common' %}


class _{{namespace.title()}}:
    {%- for package in ns_data[namespace]['packages'] %}
    {{package}}: _{{namespace.title()}}{{package.title()}}
    {%- endfor %}

    def __init__(self, proxycurl):
        self.proxycurl = proxycurl
        {%- for package in ns_data[namespace]['packages'] %}
        self.{{package}} = _{{namespace.title()}}{{package.title()}}(self)
        {%- endfor %}
{%- endif %}
{%- endfor %}


class Proxycurl(ProxycurlBase):
    {%- for namespace in ns_data %}
    {%- if namespace != 'common' %}
    {{namespace}}: _{{namespace.title()}}
    {%- endif %}
    {%- endfor %}

    def __init__(
        self,
        api_key: str = PROXYCURL_API_KEY,
        base_url: str = BASE_URL,
        timeout: int = TIMEOUT,
        max_retries: int = MAX_RETRIES,
        max_backoff_seconds: int = MAX_BACKOFF_SECONDS
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_backoff_seconds = max_backoff_seconds
        {%- for namespace in ns_data %}
        {%- if namespace != 'common' %}
        self.{{namespace}} = _{{namespace.title()}}(self)
        {%- endif %}
        {%- endfor %}


{%- for namespace in ns_data %}
{%- if namespace == 'common' %}
{%- for package in ns_data[namespace]['packages'] %}
{%- for action in ns_data[namespace]['packages'][package] %}
{{generate_method(action, ns_data[namespace]['packages'][package][action])}}
{%- endfor %}
{%- endfor %}
{%- endif %}
{%- endfor %}

