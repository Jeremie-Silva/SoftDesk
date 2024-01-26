from django.db.models import Model, SET_NULL, CASCADE, PROTECT, ForeignKey, ManyToManyField, OneToOneField, CharField, PositiveSmallIntegerField, BooleanField, DateTimeField
from django.contrib.auth.models import User


class Contributor(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="contributor")
    age = PositiveSmallIntegerField(default=18)
    can_be_contacted = BooleanField(default=False)
    can_data_be_shared = BooleanField(default=False)
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


class Project(Model):
    name = CharField(max_length=100)
    description = CharField(max_length=500, blank=True)
    author = ForeignKey(to=Contributor, on_delete=SET_NULL,
                        related_name="authored_projects", null=True)
    contributors = ManyToManyField(to=Contributor, related_name="projects_contribution")
    type = CharField(max_length=100, blank=True, choices=[
        ("BE", "Back-End"), ("FE", "Front-End"), ("IOS", "iOS"), ("AND", "Android"),
    ])
    created_time = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Issue(Model):
    project = ForeignKey(to=Project, on_delete=CASCADE, related_name="issues")
    assigned_contributor = ForeignKey(to=Contributor, on_delete=SET_NULL,
                                      related_name="assigned_issues", null=True, blank=True)
    author = ForeignKey(to=Contributor, on_delete=SET_NULL,
                        related_name="authored_issues", null=True)
    state = CharField(max_length=100, default="TO DO", choices=[
        ("TO DO", "TO DO"), ("In Progress", "In Progress"), ("Finished", "Finished"),
    ])
    priority = CharField(max_length=100, blank=True, choices=[
        ("LOW", "LOW"), ("MEDIUM", "MEDIUM"), ("HIGH", "HIGH"),
    ])
    label = CharField(max_length=100, blank=True, choices=[
        ("BUG", "BUG"), ("FEATURE", "FEATURE"), ("TASK", "TASK"),
    ])
    created_time = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.project}] {self.label} : {self.priority}"


class Comment(Model):
    issue = ForeignKey(to=Issue, on_delete=CASCADE, related_name="comments")
    author = ForeignKey(to=Contributor, on_delete=SET_NULL,
                        related_name="authored_comments", null=True)
    description = CharField(max_length=3000)
    created_time = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.author}] {self.issue}"
