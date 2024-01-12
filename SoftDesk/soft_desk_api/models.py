from django.db import models
from django.contrib.auth.models import User


class Contributor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="contributor")
    age = models.PositiveSmallIntegerField(default=18)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    is_staff = False

    @property
    def username(self):
        return self.user.username

    @property
    def project_contributions(self):
        return self.projects_contribution.all().count()

    @property
    def issue_contributions(self):
        return self.assigned_issues.all().count()

    @property
    def comments(self):
        return self.authored_comments.all().count()

    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    author = models.ForeignKey(
        to=Contributor, on_delete=models.PROTECT, related_name="authored_projects"
    )
    contributors = models.ManyToManyField(to=Contributor, related_name="projects_contribution")
    type = models.CharField(max_length=100, blank=True, choices=[
        ("BE", "Back-End"), ("FE", "Front-End"), ("IOS", "iOS"), ("AND", "Android"),
    ])
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    project = models.ForeignKey(
        to=Project, on_delete=models.PROTECT, related_name="issues"
    )
    assigned_contributor = models.ForeignKey(
        to=Contributor, on_delete=models.SET_NULL, related_name="assigned_issues",
        null=True, blank=True
    )
    author = models.ForeignKey(
        to=Contributor, on_delete=models.PROTECT, related_name="authored_issues"
    )
    state = models.CharField(max_length=100, default="TO DO", choices=[
        ("TO DO", "TO DO"), ("In Progress", "In Progress"), ("Finished", "Finished"),
    ])
    priority = models.CharField(max_length=100, blank=True, choices=[
        ("LOW", "LOW"), ("MEDIUM", "MEDIUM"), ("HIGH", "HIGH"),
    ])
    label = models.CharField(max_length=100, blank=True, choices=[
        ("BUG", "BUG"), ("FEATURE", "FEATURE"), ("TASK", "TASK"),
    ])
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.project}] {self.label} : {self.priority}"


class Comment(models.Model):
    issue = models.ForeignKey(
        to=Issue, on_delete=models.CASCADE, related_name="comments",
    )
    author = models.ForeignKey(
        to=Contributor, on_delete=models.PROTECT, related_name="authored_comments"
    )
    description = models.CharField(max_length=3000)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.author}] {self.issue}"
