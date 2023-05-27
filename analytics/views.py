from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import cache_page
from analytics import data as dataloader
from analytics import visualizations as datavis

# Create your views here.
def home(request):
    args = {"title":"SafeYou"}

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('userpage')
        else:
            args['form'] = AuthenticationForm
            return render(request, 'home.html', args)
    else:
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            args['form'] = AuthenticationForm
            args['error'] = 'Username and Password do not match'
            return render(request,'home.html',args)
        else:
            login(request,user)
            return redirect('userpage')

def about(request):
    args = {"title":"About"}
    return render(request, 'about.html',args)

def logoutaccount(request):
    logout(request)
    return redirect('home')

@cache_page(60 * 60)
def userpage(request):
    args = {"title":"Who is using our app? (User Profile)"}
    df = dataloader.get_userpage_data() # temporary
    if df is None:
        args = {"error":"Trouble fetching data at the moment."}
    else:
        vis = datavis.get_userpage_visualizations(df)
        args |= vis
    return render(request,'userpage.html',args)

#@cache_page(60 * 60 * 8)
def behaviorpage(request):
    pass

#@cache_page(60 * 60 * 8)
def stakeholderpage(request):
    pass
 