from django.db import models
from django import forms
from dbarray import IntegerArrayField

class Comment(models.Model):
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    path = IntegerArrayField(blank=True, editable=False)
    depth = models.PositiveSmallIntegerField(default=0)
    
    def __unicode__(self):
        return self.content
    
class CommentForm(forms.ModelForm):
    #Hidden value to get a child's parent
    parent = forms.CharField(widget=forms.HiddenInput(
                            attrs={'class': 'parent'}), required=False)
    
    class Meta:
        model = Comment
        fields = ('content',)