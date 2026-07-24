# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Job, Candidate
from .ai_engine import read_cv, analyze_cv
from dotenv import load_dotenv
load_dotenv()


def dashboard(request):
    jobs = Job.objects.all()
    candidates = Candidate.objects.all().order_by('-match_score')
    shortlisted = candidates.filter(status='Shortlist').count()
    rejected = candidates.filter(status='Reject').count()
    context = {
        'jobs': jobs,
        'candidates': candidates,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'total': candidates.count()
    }
    return render(request, 'dashboard.html', context)


def add_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Job.objects.create(title=title, description=description)
        messages.success(request, 'Job added successfully!')
        return redirect('dashboard')
    return render(request, 'add_job.html')


def upload_cv(request):
    jobs = Job.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        job_id = request.POST.get('job')
        cv_file = request.FILES.get('cv_file')
        job = get_object_or_404(Job, id=job_id)
        candidate = Candidate.objects.create(
            name=name,
            email=email,
            cv_file=cv_file,
            job=job
        )
        candidate.cv_file.open('rb')
        cv_text = read_cv(candidate.cv_file)
        candidate.cv_file.close()
        result = analyze_cv(cv_text, job.description)
        candidate.match_score = result['score']
        candidate.status = result['recommendation']
        candidate.ai_summary = result['summary']
        candidate.save()
        messages.success(
            request,
            f'CV analyzed! Score: {result["score"]}/100 — {result["recommendation"]}'
        )
        return redirect('dashboard')
    return render(request, 'upload_cv.html', {'jobs': jobs})


def update_status(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        candidate.status = status
        candidate.save()
        messages.success(request, f'{candidate.name} status updated to {status}!')
    return redirect('dashboard')


def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    return render(request, 'candidate_detail.html', {'candidate': candidate})