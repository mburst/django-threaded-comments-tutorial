from core.models import Comment, CommentForm
from itertools import ifilter
from django.shortcuts import render, redirect

def home(request):
    form = CommentForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            temp = form.save(commit=False)
            parent = form['parent'].value()
            
            if parent == '':
                #Set a blank path then save it to get an ID
                temp.path = []
                temp.save()
                temp.path = [temp.id]
            else:
                #Get the parent node
                node = Comment.objects.get(id=parent)
                temp.depth = node.depth + 1
                temp.path = node.path
                
                #Store parents path then apply comment ID
                temp.save()
                temp.path.append(temp.id)
                
            #Final save for parents and children
            temp.save()
            return redirect('core.views.home') 
    
    #Retrieve all comments and sort them by path
    comment_tree = Comment.objects.all().order_by('path')
                
    return render(request, 'index.html', locals())
