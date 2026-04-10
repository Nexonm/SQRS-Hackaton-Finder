"""OpenAPI response snippets shared by CRUD routers."""

PROFILE_CREATE_RESPONSES = {
    201: {"description": "Profile created"},
    409: {"description": "Handle already taken"},
    422: {"description": "Validation error (invalid role_id or skill_id)"},
}

PROFILE_GET_RESPONSES = {
    200: {"description": "Profile found"},
    404: {"description": "Profile not found"},
}

PROFILE_UPDATE_RESPONSES = {
    200: {"description": "Profile updated"},
    404: {"description": "Profile not found"},
    422: {"description": "Validation error (invalid role_id or skill_id)"},
}

PROFILE_DELETE_RESPONSES = {
    204: {"description": "Profile deleted"},
    404: {"description": "Profile not found"},
}

TEAM_CREATE_RESPONSES = {
    201: {"description": "Team created"},
    404: {"description": "Owner profile not found"},
    422: {"description": "Validation error (invalid role_id or skill_id)"},
}

TEAM_GET_RESPONSES = {
    200: {"description": "Team found"},
    404: {"description": "Team not found"},
}

TEAM_UPDATE_RESPONSES = {
    200: {"description": "Team updated"},
    403: {"description": "Not the team owner"},
    404: {"description": "Team not found"},
    422: {"description": "Validation error (invalid role_id or skill_id)"},
}

TEAM_DELETE_RESPONSES = {
    204: {"description": "Team deleted"},
    403: {"description": "Not the team owner"},
    404: {"description": "Team not found"},
}
