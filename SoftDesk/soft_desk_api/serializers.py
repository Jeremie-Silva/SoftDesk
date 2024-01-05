from rest_framework.serializers import ModelSerializer, SerializerMethodField
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

    # def create(self, validated_data):
    #     # Example: Extract nested project data from validated_data if present
    #     # projects_data = validated_data.pop('projects_contribution', None)
    #     #
    #     # # Create the Contributor instance
    #     # contributor = Contributor.objects.create(**validated_data)
    #     #
    #     # # If there's nested project data, create those projects and link to the contributor
    #     # if projects_data:
    #     #     for project_data in projects_data:
    #     #         # Create or update project instances.
    #     #         # You might need to handle nested fields within each project separately.
    #     #         Project.objects.create(contributor=contributor, **project_data)
    #     print(validated_data)
    #     return validated_data


class IssueSerializer(ModelSerializer):
    assigned_contributor = SerializerMethodField()
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
            "comments"
        ]

    def get_assigned_contributor(self, obj):
        return NestedContributorSerializer(obj.assigned_contributor).data

    def get_author(self, obj):
        return NestedContributorSerializer(obj.author).data

    def get_comments(self, obj):
        return NestedCommentSerializer(obj.comments.all(), many=True).data


class CommentSerializer(ModelSerializer):
    issue = SerializerMethodField()
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
