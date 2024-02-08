from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Contributor, Project, Issue, Comment


class ContributorField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, int):  # ID is provided
            try:
                return Contributor.objects.get(pk=data)
            except Contributor.DoesNotExist:
                raise serializers.ValidationError("Contributor with ID '{}' does not exist.".format(data))
        elif isinstance(data, str):  # Username is provided
            try:
                user = Contributor.objects.get(user__username=data)
                return user
            except (Contributor.DoesNotExist, Contributor.DoesNotExist):
                raise serializers.ValidationError("Contributor with username '{}' does not exist.".format(data))
        else:
            raise serializers.ValidationError("Invalid type for 'assigned_contributor'. Expected int (ID) or str (username).")

    def to_representation(self, value):
        return value.user.username  # Assuming Contributor model has a user field


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
    assigned_contributor = ContributorField()
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

    # def get_assigned_contributor(self, value):
    #     if isinstance(value, str):
    #         try:
    #             return Contributor.objects.get(user__username=value)
    #         except Contributor.DoesNotExist:
    #             raise serializers.ValidationError(f"Contributor with username {value} does not exist.")
    #     elif isinstance(value, int):
    #         try:
    #             Contributor.objects.get(pk=value)
    #             return value
    #         except Contributor.DoesNotExist:
    #             raise serializers.ValidationError(f"Contributor with ID {value} does not exist.")
    #     else:
    #         raise serializers.ValidationError(
    #             "Invalid input type for 'assigned_contributor'. Expected username (str) or ID (int)."
    #         )

    def get_assigned_contributor(self, obj):
        return NestedContributorSerializer(obj.assigned_contributor).data

    def get_author(self, obj):
        return NestedContributorSerializer(obj.author).data

    def get_comments(self, obj):
        return NestedCommentSerializer(obj.comments.all(), many=True).data


class CommentSerializer(ModelSerializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())
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
