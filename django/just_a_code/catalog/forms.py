# -*- coding: utf-8
from crispy_forms.bootstrap import FormActions, TabHolder, Tab, AppendedText, PrependedAppendedText

from django import forms

from file_resubmit import AdminResubmitImageWidget
from catalog.models import Category, METRO_DIST_TYPE, DEAL_PRICE_TYPE, DEAL_PRICE_PERIOD, DealType, FieldSet, Price, Location, ProductImage, Product


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Row, Field, Fieldset, Div
from regions.models import GeoLocation


class FindByIDForm(forms.Form):
    product_id = forms.IntegerField()

    def clean_product_id(self):
        product_id =  self.cleaned_data['product_id']

        try:
            Product.approved_objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise forms.ValidationError(u"Объект не найден")

        return product_id


class DealTypeForm(forms.Form):
    deal_type = forms.ModelChoiceField(queryset=DealType.objects.all(), label=u'Тип сделки')
    region = forms.ModelChoiceField(queryset=GeoLocation.objects.all(), label='Регион', empty_label=None)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(parent=None), label=u'Вид недвижимости')
    title = forms.CharField(label=u'Заголовок объявления')
    description = forms.CharField(widget=forms.widgets.Textarea, label=u'Текст объявления')
    price = forms.DecimalField(max_digits=12, decimal_places=2, label=u'Стоимость')
    price_type = forms.ChoiceField(choices=DEAL_PRICE_TYPE, required=False)
    price_period = forms.ChoiceField(choices=DEAL_PRICE_PERIOD, required=False)
    commission = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    pledge = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            u'Основная информация',
            Field('deal_type', css_class='input-xlarge'),

            Field('category', rows="3", css_class='input-xlarge'),
            Field('title', rows="3", css_class='input-xxlarge'),
            Field('description', rows="9", css_class='input-xxlarge'),
            Field('region', css_class='input-xlarge'),
            Div(
                # HTML(
                #     u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">Стоимость<span class="asteriskField">*</span></label><div class="controls">')
                # ,
                AppendedText('price', text='руб', css_class='input-small', ),
                Field('price_period', css_class='input-small', template='catalog/elements/inline_field.html'),
                Field('price_type', css_class='input-small', template='catalog/elements/inline_field.html'),

            ),
            Div(
                HTML(
                    u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">Комиссия агента<span class="asteriskField"></span></label><div class="controls">')
                ,
                Field('commission', css_class='input-small', template='catalog/elements/inline_field.html'),
                HTML(u'</div></div>'),
            ),
            Div(
                HTML(
                    u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">Залог собственника</label><div class="controls">')
                ,
                Field('pledge', css_class='input-small', template='catalog/elements/inline_field.html'),
                HTML(u'</div></div>'),
            ),
        )

    )


    def clean(self):
        cleaned_data = super(DealTypeForm, self).clean()

        if 'deal_type' in cleaned_data and not cleaned_data['deal_type'].show_price_field:
            if 'price' in self._errors:
                del self._errors["price"]

        return cleaned_data


class LocationForm(forms.ModelForm):
    region = forms.ModelChoiceField(queryset=GeoLocation.objects.all(), label='Регион', empty_label=None)
    city = forms.CharField(max_length=255, label=u'Населенный пункт')

    metro = forms.CharField(max_length=255, required=False, label=u'Метро')
    metro_dist = forms.CharField(max_length=255, required=False, label=u'До метро')
    metro_dist_type = forms.ChoiceField(choices=METRO_DIST_TYPE, required=False, label=u'Как')

    metro_alt = forms.CharField(max_length=255, required=False, label=u'Метро 2')
    metro_alt_dist = forms.CharField(max_length=255, required=False, label=u'До метро 2')
    metro_alt_dist_type = forms.ChoiceField(choices=METRO_DIST_TYPE, required=False, label=u'Как')

    address = forms.CharField(max_length=255, label=u'Адрес (улица, дом)', required=False)

    lat = forms.CharField(widget=forms.HiddenInput(), required=False)
    lng = forms.CharField(widget=forms.HiddenInput(), required=False)
    zoom_level = forms.CharField(widget=forms.HiddenInput(), required=False)
    metro_available = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            u'Месторасположение',
            Field('region', css_class='input-xlarge'),
            Field('city', css_class='input'),
            Field('address', css_class='input'),
            'lat', 'lng', 'zoom_level', 'metro_available',
            Row(
                HTML(
                    u'<div class="control-group metro"><label for="inlineCheckboxes" class="control-label">Метро</label><div class="controls">')
                ,
                Field('metro', css_class='input-small', template='catalog/elements/inline_field.html'),
                Field('metro_dist', css_class='input-medium', template='catalog/elements/inline_field.html'),
                Field('metro_dist_type', css_class='input-medium', template='catalog/elements/inline_field.html'),
                HTML(u'<br/><a href=# class="add_metro">Добавить еще одно метро</a>'),
                HTML(u'</div></div>'),
            ),
            Row(
                HTML(
                    u'<div class="control-group metro-alt"><label for="inlineCheckboxes" class="control-label">Метро 2</label><div class="controls">')
                ,
                Field('metro_alt', css_class='input-small', template='catalog/elements/inline_field.html'),
                Field('metro_alt_dist', css_class='input-medium', template='catalog/elements/inline_field.html'),
                Field('metro_alt_dist_type', css_class='input-medium', template='catalog/elements/inline_field.html'),
                HTML(u'</div></div>'),
            ),
            HTML(u'<div class="control-group"><label class="control-label">На карте:</label><div class="controls">'),
            HTML(
                u'<div class="additional_button"><a class="btn" id="geolocation" href="#">Отметить на карте</a></div></br>')
            ,
            HTML(u'<div id="map" style="width:800px; height:400px"></div>'),
            HTML(u'<p class="muted">Масштаб будет учитываться при показе карты на странице объекта</p>'),
            HTML(u'</div></div>'),
        )

    )

    def clean(self):
        cleaned_data = super(LocationForm, self).clean()
        print cleaned_data

        if cleaned_data['metro_available'] == True and cleaned_data['metro'] == '':
            msg = u"Укажите метро"
            self._errors["metro"] = self.error_class([msg])
            del cleaned_data["metro"]

        if cleaned_data['metro_available'] == True and cleaned_data['metro_dist'] == '':
            msg = u"Укажите расстояние от метро"
            self._errors["metro_dist"] = self.error_class([msg])
            del cleaned_data["metro_dist"]

        return cleaned_data


    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Location
        exclude = ('product',)


class ImageForm(forms.ModelForm):
    image = forms.ImageField(required=False, label=u'Изображение') # widget=AdminResubmitImageWidget)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Fieldset(
            Field('files-TOTAL_FORMS'),
            Field('files-INITIAL_FORMS'),
            Field('files-MAX_NUM_FORMS'),
            Field('image', css_class='input-xlarge'),
        )
    )

    class Meta:
        model = ProductImage
        exclude = ('product',)


from django.forms.formsets import formset_factory

ImageFormSet = formset_factory(ImageForm)



class FilesForm(forms.Form):
    image = forms.ImageField(widget=AdminResubmitImageWidget)

    helper = FormHelper()
    helper.form_tag = False

    helper.layout = Layout(
        Fieldset(
            u'Files',
            Field('image', css_class='input-xlarge'),
        )
    )



class DynamicForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'


    def __init__(self, *args, **kwargs):

        self.category = kwargs.pop('category', None)
        self.deal_type = kwargs.pop('deal_type', None)

        super(DynamicForm, self).__init__(*args, **kwargs)

        fsets = FieldSet.objects.filter(
            field__id__in=[x.field.id for x in self.category.fields.filter(deal_types=self.deal_type)]).distinct()

        form_field_sets = []

        for fs in fsets:

            form_field_set = Fieldset(fs.name)

            for f in self.category.fields.filter(field__field_set=fs, deal_types=self.deal_type).order_by(
                    'weight').distinct():

                field_name = 'field_%s' % f.field.id
                field_name_additional = 'field_%s_additional' % f.field.id

                if f.field.type == u'BooleanField':
                    self.fields[field_name] = forms.BooleanField(label=f.field.name, required=False)
                elif f.field.type == u'CharField':
                    self.fields[field_name] = forms.CharField(label=f.field.name, required=f.required)
                elif f.field.type == u'TextField':
                    self.fields[field_name] = forms.CharField(label=f.field.name, required=f.required,
                                                              widget=forms.Textarea)
                elif f.field.type == u'ChoiceField':
                    self.fields[field_name] = forms.ModelChoiceField(label=f.field.name, queryset=[],
                                                                     required=f.required)
                    self.fields[field_name].queryset = f.value_choice.all()

                if f.field.additional_info:
                    self.fields[field_name_additional] = forms.CharField(label=f.field.name + u' (дополнительно)',
                                                                         required=False)

                    form_field_set.fields.append(Div(
                        HTML(
                            u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">%s</label><div class="controls">' % f.field.name),
                        Field(field_name, css_class='input-medium', template='catalog/elements/inline_field.html'),
                        Field(field_name_additional, css_class='input-xlarge',
                              template='catalog/elements/inline_field.html'),
                        HTML(u'</div></div>')
                    ))
                else:
                    form_field_set.fields.append(Field(field_name, css_class=f.field.css_class))


            form_field_sets.append(form_field_set)

        self.helper.add_layout(Layout(*form_field_sets))


class PriceForm(forms.ModelForm):
    title = forms.CharField(label=u'Заголовок объявления')
    description = forms.CharField(widget=forms.widgets.Textarea, label=u'Текст объявления')


    #price_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None)
    #commission_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None)
    #pledge_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'

    class Meta:
        model = Price

    def __init__(self, *args, **kwargs):
        self.category = kwargs['instance'].product.category
        self.deal_type = kwargs['instance'].product.deal_type
        super(PriceForm, self).__init__(*args, **kwargs)



        form_field_sets = []
        form_field_set = Fieldset(u'Описание и стоимость')

        div = Div()
        div.fields.append(Field('product', type='hidden'))

        div.fields.append(Field('title', rows="3", css_class='input-xxlarge'))
        div.fields.append(Field('description', rows="9", css_class='input-xxlarge'))




        div.fields.append(AppendedText('price', text='руб.',css_class='input-small', ))
        #div.fields.append(Field('price_currency', css_class='input-medium', template='catalog/elements/inline_field.html'))

        if self.deal_type.show_period_field:
            div.fields.append(Field('price_period', css_class='input-small', template='catalog/elements/inline_field.html'))
        else:
            div.fields.append(Field('price_period', css_class='input-small', type='hidden', template='catalog/elements/inline_field.html'))

        if self.category.show_additional_price_options:
            div.fields.append(Field('price_type', css_class='input-small', template='catalog/elements/inline_field.html'))
        else:
            div.fields.append(Field('price_type', css_class='input-small', type='hidden', template='catalog/elements/inline_field.html'))


        form_field_set.fields.append(div)

        if self.deal_type.show_commission_field:
            div_commission = Div()
        else:
            div_commission = Div(style='display: none')

        div_commission.fields = (
            HTML(
                u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">Комиссия агента<span class="asteriskField"></span></label><div class="controls">')
            ,
            Field('commission', css_class='input-small', template='catalog/elements/inline_field.html'),
            #Field('commission_currency', css_class='input-medium', template='catalog/elements/inline_field.html'),
            HTML(u'</div></div>'),
            )

        form_field_set.fields.append(div_commission)

        if self.deal_type.show_pledge_field:
            div_pledge = Div()
        else:
            div_pledge = Div(style='display: none')

        div_pledge.fields = (Div(
            HTML(
                u'<div class="control-group"><label for="inlineCheckboxes" class="control-label">Залог собственника</label><div class="controls">')
            ,
            Field('pledge', css_class='input-small', template='catalog/elements/inline_field.html'),
            #Field('pledge_currency', css_class='input-medium', template='catalog/elements/inline_field.html'),
            HTML(u'</div></div>'),
            ))

        form_field_set.fields.append(div_pledge)

        form_field_sets.append(form_field_set)

        self.helper.add_layout(Layout(*form_field_sets))


class DemandForm(forms.ModelForm):
    title = forms.CharField(label=u'Заголовок')
    description = forms.CharField(widget=forms.widgets.Textarea, label=u'Текст')
    region = forms.ModelChoiceField(queryset=GeoLocation.objects.all(), label='Регион', empty_label=None)

    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        TabHolder(
        Tab(
            u'Заголовок обращения и текст',
            Field('title', rows="3", css_class='input-xlarge', style='width: 500px'),
            Field('description', rows="9", css_class='input-xlarge', style='width: 500px'),
            css_id='main',
            ),
        Tab(
            u'Дополнительные параметры',
            Field('category', rows="9", css_class=''),
            Field('region', rows="9", css_class='input-large'),
            css_id='ext'
            )
        )
    )

    class Meta:
        model = Product
        fields = ('title', 'description', 'category')
