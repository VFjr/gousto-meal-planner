import { useState } from 'react';
import './App.css';

type SearchType = 'url' | 'name' | 'ingredient';

export default function App() {
  const [searchType, setSearchType] = useState<SearchType>('name');
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    console.log(`Searching by ${searchType}:`, searchQuery);
    // Implement your search logic here
  };

  return (
    <div className="container">
      <div className="toggle-container">
        <button
          className={`toggle-button ${searchType === 'url' ? 'active' : ''}`}
          onClick={() => setSearchType('url')}
        >
          URL
        </button>
        <button
          className={`toggle-button ${searchType === 'name' ? 'active' : ''}`}
          onClick={() => setSearchType('name')}
        >
          Name
        </button>
        <button
          className={`toggle-button ${searchType === 'ingredient' ? 'active' : ''}`}
          onClick={() => setSearchType('ingredient')}
        >
          Ingredient
        </button>
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
    </div>
  );
}
