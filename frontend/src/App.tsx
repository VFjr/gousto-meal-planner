import { useState, useEffect } from 'react';
import './App.css';
import { Recipe, SearchType } from './types';
import { getRecipeBySlug, getRecipesList, RecipeListItem } from './services/api';
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
  const [isDropdownActive, setIsDropdownActive] = useState(true);

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

  const handleRecipeSelect = async (selectedRecipe: RecipeListItem) => {
    setSearchQuery(selectedRecipe.title);
    setIsDropdownActive(false);
    await handleSearch(selectedRecipe.slug);
  };

  useEffect(() => {
    setIsDropdownActive(true);
  }, [searchType]);

  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setIsDropdownActive(true);
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
    setLoading(true);

    try {
      if (searchType === 'url') {
        const extractedSlug = extractSlugFromUrl(searchQuery);
        if (!extractedSlug) {
          throw new Error('Invalid URL format');
        }
        const recipeData = await getRecipeBySlug(extractedSlug);
        setRecipe(recipeData);
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
          {searchType === 'name' && (
            <SearchDropdown
              items={recipeList}
              searchQuery={searchQuery}
              onSelect={handleRecipeSelect}
              isActive={isDropdownActive}
              onClose={() => setIsDropdownActive(false)}
            />
          )}
        </div>

        <div className="divider">OR</div>
        <button onClick={() => console.log('Surprise!')} className="surprise-button">
          🎲 Surprise Me!
        </button>
      </div>

      <div className="recipes-section">
        {loading && <LoadingSpinner />}
        {error && <div className="error-message">{error}</div>}
        {recipe && <RecipeCard recipe={recipe} isSingleRecipe={true} />}
      </div>
    </div>
  );
}
