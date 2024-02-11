from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer, SerializerMethodField, PrimaryKeyRelatedField
from .fields import ContributorField
from .models import Contributor, Project, Issue, Comment


class NestedContributorSerializer(ModelSerializer):
    class Meta:
        model = Contributor
        fields = [
            "id",
            "username",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "authored_projects",
            "projects_contribution",
            "assigned_issues",
            "authored_issues",
            "authored_comments"
        ]


class NestedProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "author",
            "contributors",
            "type",
            "created_time",
            "issues"
        ]


class NestedIssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "project",
            "assigned_contributor",
            "author",
            "state",
            "priority",
            "label",
            "created_time",
            "comments"
        ]


class NestedCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "issue",
            "author",
            "description",
            "created_time"
        ]


class ContributorSerializer(ModelSerializer):
    authored_projects = SerializerMethodField()
    projects_contribution = SerializerMethodField()
    assigned_issues = SerializerMethodField()
    authored_issues = SerializerMethodField()
    authored_comments = SerializerMethodField()

    class Meta:
        model = Contributor
        fields = [
            "id",
            "username",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "authored_projects",
            "projects_contribution",
            "assigned_issues",
            "authored_issues",
            "authored_comments"
        ]

    def get_authored_projects(self, obj):
        return NestedProjectSerializer(obj.authored_projects.all(), many=True).data

    def get_projects_contribution(self, obj):
        return NestedProjectSerializer(obj.projects_contribution.all(), many=True).data

    def get_assigned_issues(self, obj):
        return NestedIssueSerializer(obj.assigned_issues.all(), many=True).data

    def get_authored_issues(self, obj):
        return NestedIssueSerializer(obj.authored_issues.all(), many=True).data

    def get_authored_comments(self, obj):
        return NestedCommentSerializer(obj.authored_comments.all(), many=True).data


class ProjectSerializer(ModelSerializer):
    author = SerializerMethodField()
    contributors = SerializerMethodField()
    issues = SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "author",
            "contributors",
            "type",
            "created_time",
            "issues"
        ]

    def get_author(self, obj):
        return NestedContributorSerializer(obj.author).data

    def get_contributors(self, obj):
        return NestedContributorSerializer(obj.contributors.all(), many=True).data

    def get_issues(self, obj):
        return NestedIssueSerializer(obj.issues.all(), many=True).data


class IssueSerializer(ModelSerializer):
    assigned_contributor = ContributorField(required=False, allow_null=True)
    author = SerializerMethodField()
    comments = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "id",
            "project",
            "assigned_contributor",
            "author",
            "state",
            "priority",
            "label",
            "created_time",
            "comments",
        ]

    def validate(self, attrs):
        attrs["author"] = self.context["request"].user.contributor
        if not attrs.get("assigned_contributor"):
            attrs["assigned_contributor"] = self.context["request"].user.contributor
        if not attrs.get("project"):
            attrs["project"] = self.instance.project

        if attrs["author"] not in attrs["project"].contributors.all() \
                and attrs["author"] != attrs["project"].author:
            raise PermissionDenied("You are not contributor or author of this project.")
        if attrs["assigned_contributor"] not in attrs["project"].contributors.all() \
                and attrs["assigned_contributor"] != attrs["project"].author:
            raise PermissionDenied(
                "Assigned contributor is not a contributor or author of this project."
            )
        return attrs

    def get_assigned_contributor(self, obj):
        return NestedContributorSerializer(obj.assigned_contributor).data

    def get_author(self, obj):
        return NestedContributorSerializer(obj.author).data

    def get_comments(self, obj):
        return NestedCommentSerializer(obj.comments.all(), many=True).data


class CommentSerializer(ModelSerializer):
    issue = PrimaryKeyRelatedField(queryset=Issue.objects.all())
    author = SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "issue",
            "author",
            "description",
            "created_time"
        ]

    def get_issue(self, obj):
        return NestedIssueSerializer(obj.issue).data

    def get_author(self, obj):
        return NestedContributorSerializer(obj.author).data

    def validate(self, attrs):
        attrs["author"] = self.context["request"].user.contributor
        if not attrs.get("issue"):
            attrs["issue"] = Comment.objects.get(pk=self.context["view"].kwargs["pk"]).issue
        if attrs["author"] not in attrs["issue"].project.contributors.all() \
                and attrs["author"] != attrs["issue"].project.author:
            raise PermissionDenied("You are not contributor or author of this project.")
        return attrs
