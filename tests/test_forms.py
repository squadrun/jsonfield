from django.forms import ModelForm
from django.test import TestCase

from .models import JSONNotRequiredModel


class JSONModelFormTest(TestCase):
    def setUp(self):
        class JSONNotRequiredForm(ModelForm):
            class Meta:
                model = JSONNotRequiredModel
                fields = '__all__'

        self.form_class = JSONNotRequiredForm

    def test_blank_form(self):
        form = self.form_class(data={'json': ''})
        self.assertFalse(form.has_changed())

    def test_form_with_data(self):
        form = self.form_class(data={'json': '{}'})
        self.assertTrue(form.has_changed())

    def test_form_save(self):
        form = self.form_class(data={'json': ''})
        form.save()

    def test_save_values(self):
        values = [
            # (type, form input, db value)
            ('object', '{"a": "b"}', {'a': 'b'}),
            ('array', '[1, 2]', [1, 2]),
            ('string', '"test"', 'test'),
            ('float', '1.2', 1.2),
            ('int', '1234', 1234),
            ('bool', 'true', True),
            ('null', 'null', None),
        ]

        for vtype, form_value, db_value in values:
            with self.subTest(type=vtype, input=form_value, db=db_value):
                form = self.form_class(data={'json': form_value})
                self.assertTrue(form.is_valid(), msg=form.errors)

                instance = form.save()
                self.assertEqual(instance.json, db_value)

    def test_render_values(self):
        values = [
            # (type, db value, form output)
            ('object', {'a': 'b'}, '{\n    "a": "b"\n}'),
            ('array', [1, 2], "[\n    1,\n    2\n]"),
            ('string', 'test', '"test"'),
            ('float', 1.2, '1.2'),
            ('int', 1234, '1234'),
            ('bool', True, 'true'),
            ('null', None, 'null'),
        ]

        for vtype, db_value, form_value in values:
            with self.subTest(type=vtype, db=db_value, output=form_value):
                instance = JSONNotRequiredModel.objects.create(json=db_value)

                form = self.form_class(instance=instance)
                self.assertEqual(form['json'].value(), form_value)

    def test_invalid_value(self):
        form = self.form_class(data={'json': 'foo'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'json': ['"foo" value must be valid JSON.'],
        })
        self.assertEqual(form['json'].value(), 'foo')
