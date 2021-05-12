#!/usr/bin/env python3
import os

from aws_cdk import core

from cdk_pr_stepfunctions.cdk_pr_stepfunctions_stack import CdkPrStepfunctionsStack


app = core.App()
CdkPrStepfunctionsStack(app, "CdkPrStepfunctionsStack",)

app.synth()
