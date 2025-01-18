import { useState, useEffect } from 'react';
import './App.css';
import './components/Search.css';
import { Recipe, SearchType } from './types';
import { getRecipeBySlug, getRecipesList, RecipeListItem, getIngredientsList, getRecipesByIngredient, Ingredient } from './services/api';
import { RecipeCard } from './components/RecipeCard';
import { LoadingSpinner } from './components/LoadingSpinner';
import { SearchDropdown } from './components/SearchDropdown';

export default function App() {
  const [searchType, setSearchType] = useState<SearchType>('url');
  const [searchQuery, setSearchQuery] = useState('');
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [recipeList, setRecipeList] = useState<RecipeListItem[]>([]);
  const [ingredientsList, setIngredientsList] = useState<Ingredient[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [visibleRecipes, setVisibleRecipes] = useState(6);
  const [recipeListItems, setRecipeListItems] = useState<RecipeListItem[]>([]);

  useEffect(() => {
    const loadRecipes = async () => {
      try {
        const recipes = await getRecipesList();
        setRecipeList(recipes);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load recipes');
      }
    };

    loadRecipes();
  }, []);

  useEffect(() => {
    const loadIngredients = async () => {
      try {
        const ingredients = await getIngredientsList();
        setIngredientsList(ingredients);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load ingredients');
      }
    };

    loadIngredients();
  }, []);

  const handleRecipeSelect = async (selectedRecipe: RecipeListItem) => {
    await handleSearch(selectedRecipe.slug);
    setSearchQuery('');
  };

  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const extractSlugFromUrl = (url: string): string | null => {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/');
      return pathParts[pathParts.length - 1];
    } catch {
      return null;
    }
  };

  const handleSearch = async (slug?: string) => {
    setError(null);
    setRecipe(null);
    setRecipes([]);
    setLoading(true);

    try {
      if (searchType === 'url') {
        const extractedSlug = extractSlugFromUrl(searchQuery);
        if (!extractedSlug) {
          throw new Error('Invalid URL format');
        }
        const recipeData = await getRecipeBySlug(extractedSlug);
        setRecipe(recipeData);
        setSearchQuery('');
      } else if (searchType === 'name' && slug) {
        const recipeData = await getRecipeBySlug(slug);
        setRecipe(recipeData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSurpriseMe = async () => {
    if (recipeList.length === 0) return;

    setError(null);
    setRecipe(null);
    setRecipes([]);
    setLoading(true);
    setVisibleRecipes(6);

    try {
      const randomIndex = Math.floor(Math.random() * recipeList.length);
      const randomRecipe = recipeList[randomIndex];
      const recipeData = await getRecipeBySlug(randomRecipe.slug);
      setRecipe(recipeData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleIngredientSelect = async (ingredient: Ingredient) => {
    setSearchQuery(ingredient.name);
    setError(null);
    setRecipe(null);
    setRecipes([]);
    setRecipeListItems([]);
    setLoading(true);
    setVisibleRecipes(6);

    try {
      const recipesList = await getRecipesByIngredient(ingredient.id);
      setRecipeListItems(recipesList);

      // Only fetch details for first batch of visible recipes
      const initialRecipes = await Promise.all(
        recipesList.slice(0, 6).map(item => getRecipeBySlug(item.slug))
      );
      setRecipes(initialRecipes);
      setSearchQuery('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = async () => {
    const nextBatch = recipeListItems.slice(visibleRecipes, visibleRecipes + 6);
    setLoading(true);

    try {
      const newRecipes = await Promise.all(
        nextBatch.map(item => getRecipeBySlug(item.slug))
      );
      setRecipes(prev => [...prev, ...newRecipes]);
      setVisibleRecipes(prev => prev + 6);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">Gousto Recipe Finder</h1>
      <div className="search-section">
        <div className="toggle-container">
          <button
            className={`toggle-button ${searchType === 'url' ? 'active' : ''}`}
            onClick={() => setSearchType('url')}
          >URL</button>
          <button
            className={`toggle-button ${searchType === 'name' ? 'active' : ''}`}
            onClick={() => setSearchType('name')}
          >Name</button>
          <button
            className={`toggle-button ${searchType === 'ingredient' ? 'active' : ''}`}
            onClick={() => setSearchType('ingredient')}
          >Ingredient</button>
        </div>

        <div className="search-container">
          <input
            type="text"
            placeholder={`Search by ${searchType}...`}
            value={searchQuery}
            onChange={handleSearchInputChange}
            className="search-input"
          />
          <button onClick={() => handleSearch()} className="search-button">
            Search
          </button>
          {searchType === 'name' && searchQuery && (
            <SearchDropdown
              items={recipeList}
              searchQuery={searchQuery}
              onSelect={(item) => handleRecipeSelect(item as RecipeListItem)}
              onClose={() => setSearchQuery('')}
              type="recipe"
            />
          )}
          {searchType === 'ingredient' && searchQuery && (
            <SearchDropdown
              items={ingredientsList}
              searchQuery={searchQuery}
              onSelect={(item) => handleIngredientSelect(item as Ingredient)}
              onClose={() => setSearchQuery('')}
              type="ingredient"
            />
          )}
        </div>

        <div className="divider">OR</div>
        <button onClick={() => handleSurpriseMe()} className="surprise-button">
          🎲 Surprise Me!
        </button>
      </div>

      <div className="recipes-section">
        {loading && <LoadingSpinner />}
        {error && <div className="error-message">{error}</div>}
        {recipe && <RecipeCard recipe={recipe} isSingleRecipe={true} />}
        {recipes.slice(0, visibleRecipes).map(recipe => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
        {recipes.length > 0 && recipeListItems.length > visibleRecipes && (
          <button
            className="load-more-button"
            onClick={handleLoadMore}
          >
            Load More
          </button>
        )}
      </div>
    </div>
  );
}
