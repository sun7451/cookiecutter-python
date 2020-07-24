import os
import re

import pytest
import sh
from binaryornot.check import is_binary

cookiecutter_variable_pattern = re.compile(r"{{(\s?cookiecutter)[.](.*?)}}")

SUPPORTED_COMBINATIONS = [
    {"index_server": "none", "use_pipenv": "y"},
    {"index_server": "none", "use_pipenv": "n"},
    {"index_server": "aliyun", "use_pipenv": "y"},
    {"index_server": "aliyun", "use_pipenv": "n"},
    {"index_server": "tendata", "use_pipenv": "y"},
    {"index_server": "tendata", "use_pipenv": "n"},
    {"ci_tools": "none"},
    {"ci_tools": "Gitlab"},
    {"ci_tools": "Github"},
    {"use_src_layout": "y"},
    {"use_src_layout": "n"},
]


def _fixture_id(ctx):
    """Helper to get a user friendly test name from the parametrized context."""
    return "-".join(f"{key}:{value}" for key, value in ctx.items())


def build_files_list(root_dir):
    """Build a list containing absolute paths to the generated files."""
    return [
        os.path.join(dirpath, file_path)
        for dirpath, subdirs, files in os.walk(root_dir)
        for file_path in files
    ]


def check_paths(paths):
    """Method to check all paths have correct substitutions."""
    # Assert that no match is found in any of the files
    for path in paths:
        if is_binary(path):
            continue

        for line in open(path, "r"):
            match = cookiecutter_variable_pattern.search(line)
            msg = "cookiecutter variable not replaced in {}"
            assert match is None, msg.format(path)


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_project_generation(cookies, context_override):
    """Test that project is generated and fully rendered."""
    result = cookies.bake(extra_context={**context_override})
    assert result.exit_code == 0
    assert result.project.isdir()
    assert result.exception is None

    paths = build_files_list(str(result.project))
    assert paths
    check_paths(paths)


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_flake8_passes(cookies, context_override):
    """Generated project should pass flake8."""
    result = cookies.bake(extra_context=context_override)

    try:
        sh.flake8(_cwd=str(result.project))
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout.decode())


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_isort_passes(cookies, context_override):
    """Generated project should pass flake8."""
    result = cookies.bake(extra_context=context_override)

    try:
        sh.isort(_cwd=str(result.project))
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout.decode())


@pytest.mark.parametrize(
    ["use_dicker", "expected_result"], [("y", [True, True]), ("n", [False, False])]
)
def test_docker_invokes(cookies, use_dicker, expected_result):
    result = cookies.bake(extra_context={"use_docker": use_dicker})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()
    exist = [
        os.path.isfile(os.path.join(str(result.project), "Dockerfile")),
        os.path.isfile(os.path.join(str(result.project), ".dockerignore")),
    ]
    assert exist == expected_result


@pytest.mark.parametrize(
    ["use_pipenv", "index_server", "expected_result"],
    [
        ("y", "none", ["Pipfile", "pypi"]),
        ("n", "none", ["requirements.txt", ""]),
        ("y", "aliyun", ["Pipfile", "aliyun"]),
        ("n", "aliyun", ["requirements.txt", "aliyun"]),
        ("y", "tendata", ["Pipfile", "tendata"]),
        ("n", "tendata", ["requirements.txt", "tendata"]),
    ],
)
def test_index_server_invokes(cookies, use_pipenv, index_server, expected_result):
    result = cookies.bake(
        extra_context={"use_pipenv": use_pipenv, "index_server": index_server}
    )

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()

    assert os.path.isfile(os.path.join(str(result.project), expected_result[0]))
    with open(os.path.join(str(result.project), expected_result[0]), "r") as file:
        data = file.read()
        assert expected_result[1] in data


@pytest.mark.parametrize(
    ["use_src_layout", "except_value"], [("y", True), ("n", False),]
)
def test_use_src_layout_invokes(cookies, use_src_layout, except_value):
    result = cookies.bake(extra_context={"use_src_layout": use_src_layout})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()
    assert os.path.exists(os.path.join(result.project, "src")) == except_value


@pytest.mark.parametrize(["ci_tools", "expect_value"], [("none", ""),])
def test_ci_tools_invokes(cookies, ci_tools, expect_value):
    result = cookies.bake(extra_context={"ci_tools": ci_tools})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()
    assert os.path.exists(os.path.join(result.project, expect_value))
