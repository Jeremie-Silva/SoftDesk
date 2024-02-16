from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer, SerializerMethodField, PrimaryKeyRelatedField, CharField, ValidationError
from .fields import ContributorField
from .models import Contributor, Project, Issue, Comment, User


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
    username = CharField()
    password = CharField(write_only=True)

    class Meta:
        model = Contributor
        fields = [
            "id",
            "username",
            "password",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "project_contributions",
            "issue_contributions",
            "comments",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists() and \
                self.context["request"].user != User.objects.filter(username=value).first():
            raise ValidationError("This username is already taken.")
        return value

    def validate_age(self, value):
        if value < 15:
            raise ValidationError("You must have 16 years old, for use this application.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        user = User.objects.create(
            username=username, password=make_password(password)
        )
        return Contributor.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("username") is not None:
            instance.user.username = validated_data.get("username")
            instance.user.save()
        if validated_data.get("password") is not None:
            instance.user.password = make_password(validated_data.get("password"))
            instance.user.save()
        instance.age = validated_data.get("age", instance.age)
        instance.can_be_contacted = validated_data.get("can_be_contacted", instance.can_be_contacted)
        instance.can_data_be_shared = validated_data.get("can_data_be_shared", instance.can_data_be_shared)
        instance.save()
        return instance


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
