def test_smoke_integration():
    assert True


def test_pytest_options(request, project_short_tag):
    keep_image = request.config.getoption("--keep-saas-database")
    db_id = request.config.getoption("--saas-database-id")
    st = project_short_tag
    print(f'\nkeep_image: {keep_image}, db ID: {db_id}, project_short_tag: "{st}"')


# def test_existing_database(saas_database):
#     db = saas_database
#     print(f'ID: {db.id}')


def test_fixture(saas_database):
    assert True
