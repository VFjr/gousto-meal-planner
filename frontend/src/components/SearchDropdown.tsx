import Fuse from 'fuse.js';
import { RecipeListItem } from '../services/api';
import { useEffect, useRef, useState } from 'react';

interface SearchDropdownProps {
    items: RecipeListItem[];
    searchQuery: string;
    onSelect: (item: RecipeListItem) => void;
    onClose: () => void;
}

export function SearchDropdown({ items, searchQuery, onSelect, onClose }: SearchDropdownProps) {
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fuse = new Fuse(items, {
        keys: ['title'],
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

    const handleSelect = (item: RecipeListItem) => {
        onSelect(item);
        onClose();
    };

    if (results.length === 0) return null;

    return (
        <div className="search-dropdown" ref={dropdownRef}>
            {results.map(({ item }) => (
                <div
                    key={item.slug}
                    className="search-dropdown-item"
                    onClick={() => handleSelect(item)}
                >
                    {item.title}
                </div>
            ))}
        </div>
    );
} 