import { useState } from 'react';
import './App.css';
import { Recipe, SearchType } from './types';
import { getRecipeBySlug } from './services/api';
import { RecipeCard } from './components/RecipeCard';

export default function App() {
  const [searchType, setSearchType] = useState<SearchType>('url');
  const [searchQuery, setSearchQuery] = useState('');
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const extractSlugFromUrl = (url: string): string | null => {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/');
      return pathParts[pathParts.length - 1];
    } catch {
      return null;
    }
  };

  const handleSearch = async () => {
    setError(null);
    setRecipe(null);
    setLoading(true);

    try {
      if (searchType === 'url') {
        const slug = extractSlugFromUrl(searchQuery);
        if (!slug) {
          throw new Error('Invalid URL format');
        }
        const recipeData = await getRecipeBySlug(slug);
        setRecipe(recipeData);
      }
      // Future implementation for name and ingredient search
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
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button">
            Search
          </button>
        </div>

        <div className="divider">OR</div>
        <button onClick={() => console.log('Surprise!')} className="surprise-button">
          🎲 Surprise Me!
        </button>
      </div>

      <div className="recipes-section">
        {loading && <div>Loading...</div>}
        {error && <div className="error-message">{error}</div>}
        {recipe && <RecipeCard recipe={recipe} />}
      </div>
    </div>
  );
}
