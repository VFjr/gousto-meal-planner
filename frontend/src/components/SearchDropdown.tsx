import Fuse from 'fuse.js';
import { RecipeListItem, Ingredient } from '../services/api';
import { useEffect, useRef } from 'react';
import './SearchDropdown.css';

interface SearchDropdownProps {
    items: (RecipeListItem | Ingredient)[];
    searchQuery: string;
    onSelect: (item: RecipeListItem | Ingredient) => void;
    onClose: () => void;
    type: 'recipe' | 'ingredient';
}

export function SearchDropdown({ items, searchQuery, onSelect, onClose, type }: SearchDropdownProps) {
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fuse = new Fuse(items, {
        keys: [type === 'recipe' ? 'title' : 'name'],
        threshold: 0.3,
    });

    const results = searchQuery
        ? fuse.search(searchQuery).slice(0, 5)
        : [];

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                onClose();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [onClose]);

    if (results.length === 0) return null;

    return (
        <div className="search-dropdown" ref={dropdownRef}>
            {results.map(({ item }) => (
                <div
                    key={type === 'recipe' ? (item as RecipeListItem).slug : (item as Ingredient).id}
                    className="search-dropdown-item"
                    onClick={() => onSelect(item)}
                >
                    {type === 'recipe' ? (item as RecipeListItem).title : (item as Ingredient).name}
                </div>
            ))}
        </div>
    );
} 