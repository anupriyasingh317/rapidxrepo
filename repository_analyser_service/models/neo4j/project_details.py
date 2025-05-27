from typing import List
from uuid import uuid4
from xmlrpc.client import DateTime

from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    ArrayProperty

)

class ProjectDetails(StructuredNode):
    key = StringProperty(unique_index=True, default=uuid4)
    name = StringProperty()
    organization = StringProperty()
    description = StringProperty()
    project_id = IntegerProperty()
    run_id = IntegerProperty()

    technology = StringProperty()
    line_of_business = StringProperty()
    sector = StringProperty()
    focus_area = StringProperty()
    encoding_type = StringProperty()
    repo_url = StringProperty()
    repo_name = StringProperty()
    branch = StringProperty()

    goals = StringProperty(default="")
    functional_modules = StringProperty(default="")
    actors = StringProperty()
    roots = ArrayProperty(default=[])

class UserVerifiedGroups(StructuredNode):
    key = StringProperty(unique_index=True, default=uuid4)
    project_id = IntegerProperty()
    run_id = IntegerProperty()
    type = StringProperty(default="UserVerifiedGroups")
    name = StringProperty()
    description = StringProperty()
