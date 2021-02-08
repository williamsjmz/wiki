import secrets
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from markdown import Markdown
from django import forms
from django.urls import reverse



class NewEntry(forms.Form):
    title = forms.CharField(label='Entry title', widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

    

def index(request):
    if "title" not in request.session:
        request.session["title"] = []
    if "content" not in request.session:
        request.session["content"] = []

    return render(request, "encyclopedia/index.html", {
        "entries": request.session["title"]
    })



def entry(request, entry):
    entry_content = util.get_entry(entry)
    
    if entry_content is not None and entry.upper() in [x.upper() for x in request.session["title"]]:
        markdown = Markdown()
        return render(request, "encyclopedia/entry.html", {
            "entry_title": entry,
            "entry_content": markdown.convert(entry_content)
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry,
            "error_message": "This web page was not found."
        })



def search(request):
    if request.method == "GET":
        query_parameter = request.GET.get('q', '')
        if query_parameter.upper() in [x.upper() for x in request.session["title"]]:
            markdown = Markdown()
            return render(request, "encyclopedia/entry.html", {
                "entry_title": query_parameter,
                "entry_content": markdown.convert(util.get_entry(query_parameter))
            })
        else:
            subStringEntries = []
            for entry in request.session["title"]:
                if query_parameter.upper() in entry.upper():
                    subStringEntries.append(entry)

            if len(subStringEntries) > 0:
                return render(request, "encyclopedia/index.html", {
                    "entries": subStringEntries,
                    "search": True,
                    "entry": query_parameter
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "entry_title": query_parameter,
                    "error_message": f"No results found for {query_parameter}"
                })



def new(request):
    if request.method == 'POST':
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            edit = form.cleaned_data["edit"]
            if title.upper() not in [x.upper() for x in request.session["title"]] and edit is not True:
                request.session["title"] += [title]
                request.session["content"] += [content]
                util.save_entry(title, content)     
                return HttpResponseRedirect(reverse("wiki:new"))    
            elif edit is True:
                for i in range(len(request.session["title"])):
                    if title.upper() == request.session["title"][i].upper():
                        request.session["content"][i] = content
                        util.save_entry(title, content)
                        break
                return HttpResponseRedirect(reverse("wiki:entry", args=[title]))
            else:
                return render(request, "encyclopedia/error.html", {
                    "entry_title": "Error",
                    "error_message": f"The {title} page already exists."
                })
        else:
            return render(request, "encyclopedia/newpage.html", {
               "form": form,
               "entry_title": "New Entry"
            })
    return render(request, "encyclopedia/newpage.html", {
        "form": NewEntry(),
        "entry_title": "New Entry"
    })



def edit(request, entry):
    entry_content = util.get_entry(entry)
    if entry_content is None:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry,
            "error_message": "This web page was not found"
        })
    else:
        form = NewEntry()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entry_content
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newpage.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entry_title": form.fields["title"].initial
        })



def random(request):
    entries = request.session["title"]
    if len(entries) == 0:
        return HttpResponseRedirect(reverse("wiki:index"))
    else:
        entry = secrets.choice(entries)
        return HttpResponseRedirect(reverse("wiki:entry", args=[entry]))

