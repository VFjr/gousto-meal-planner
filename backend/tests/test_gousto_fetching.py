
import pytest

import src.gousto_fetcher as fetcher

# Note that these tests use Gousto API endpoints, so they will fail if their API is down


@pytest.mark.asyncio
async def test_get_recipe_stubs_from_page():
    recipe_stubs = await fetcher.get_recipe_slugs_from_page(0)

    assert isinstance(recipe_stubs, list)
    assert len(recipe_stubs) == fetcher.constants.GET_RECIPES_PAGE_LIMIT
    assert all(isinstance(stub, str) for stub in recipe_stubs)
    assert all("/" not in stub for stub in recipe_stubs)

    recipe_stubs = await fetcher.get_recipe_slugs_from_page(20)
    assert isinstance(recipe_stubs, list)
    assert len(recipe_stubs) == fetcher.constants.GET_RECIPES_PAGE_LIMIT
    assert all(isinstance(stub, str) for stub in recipe_stubs)
    assert all("/" not in stub for stub in recipe_stubs)


@pytest.mark.asyncio
async def test_no_more_recipes():
    with pytest.raises(fetcher.errors.NoMoreRecipesError):
        await fetcher.get_recipe_slugs_from_page(100000)
