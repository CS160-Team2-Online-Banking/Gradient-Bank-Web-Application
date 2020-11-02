from django import forms


class SearchForm(forms.Form):
    title = forms.CharField(
        initial='',
        label='title',
        required=False,  # 必須ではない
    )
    text = forms.CharField(
        initial='',
        label='text',
        required=False,  # 必須ではない
    )
