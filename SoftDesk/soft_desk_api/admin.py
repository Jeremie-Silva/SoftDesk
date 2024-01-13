from django.contrib.admin import register, ModelAdmin
from .models import Contributor, Project, Issue, Comment


@register(Contributor)
class ContributorAdmin(ModelAdmin):
    list_display = ("username", "age", "project_contributions", "issue_contributions", "comments", "can_be_contacted", "can_data_be_shared")
    fields = ("user", "age", "can_be_contacted")


@register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("name", "author", "type", "display_contributors", "created_time")
    fields = ("name", "author", "type", "contributors")

    def display_contributors(self, obj):
        return ", ".join(
            [contributor.username for contributor in obj.contributors.all()]
        )
    display_contributors.short_description = "contributors"


@register(Issue)
class IssueAdmin(ModelAdmin):
    list_display = ("project", "author", "assigned_contributor", "state", "priority", "label", "created_time")
    fields = ("author", "project", "assigned_contributor", "state", "priority", "label")


@register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("description", "author", "issue", "created_time")
    fields = ("issue", "author", "description")
