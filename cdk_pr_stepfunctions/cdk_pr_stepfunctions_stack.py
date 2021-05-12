from aws_cdk import (
    aws_stepfunctions as _step_fn,
    aws_stepfunctions_tasks as _tasks,
    aws_codebuild as _codebuild,
    aws_codecommit as codecommit
)
from aws_cdk.core import (
    Stack,
    Construct,
    Duration
)


class CdkPrStepfunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = codecommit.Repository(
            self,
            "repo",
            repository_name="demorepo",
            description="Repo to test PR with stepfunctions"
        )

        proj1 = self.new_build_project(repo, "pr_specs/buildspec.yaml", "proj1")

        proj2 = _codebuild.Project(
            self,
            "proj_name",
            badge=True,
            description="Build project for ",
            environment=_codebuild.BuildEnvironment(
                build_image=_codebuild.LinuxBuildImage.STANDARD_5_0,
                compute_type=_codebuild.ComputeType.LARGE,
                privileged=True
            ),
            project_name="proj_name",
            build_spec=_codebuild.BuildSpec.from_source_filename(
                filename="pr_specs/buildspec2.yaml"
            ),
            timeout=Duration.minutes(10),
        )

        input_task = _step_fn.Pass(
            self,
            "passstate"
        )

        proj1_tasks = self.new_codebuild_task(proj1)
        proj2_tasks = self.new_codebuild_task(proj2)

        definition = input_task.next(proj1_tasks).next(proj2_tasks)

        _fn = _step_fn.StateMachine(
            self,
            "statemachine",
            definition=definition,
            state_machine_name="statemachine",
        )

    def new_codebuild_task(self, project:_codebuild.Project) -> _tasks.CodeBuildStartBuild:
        return _tasks.CodeBuildStartBuild(
            self,
            f"{project}task",
            project=project,
            timeout=Duration.minutes(10),
            integration_pattern=_step_fn.IntegrationPattern.RUN_JOB
        )

    def new_build_project(self, repo: codecommit.Repository, buildspec_path: str, proj_name: str) -> _codebuild.Project:
        return _codebuild.Project(
            self,
            proj_name,
            badge=True,
            source=_codebuild.Source.code_commit(
                repository=repo
            ),
            description=f"Build project for {proj_name}",
            environment=_codebuild.BuildEnvironment(
                build_image=_codebuild.LinuxBuildImage.STANDARD_5_0,
                compute_type=_codebuild.ComputeType.LARGE,
                privileged=True
            ),
            project_name=proj_name,
            build_spec=_codebuild.BuildSpec.from_source_filename(
                filename=buildspec_path
            ),
            timeout=Duration.minutes(10)
        )
