import { Recipe } from '../types';
import { getProxiedImageUrl } from '../utils/image';
import { useEffect, useState } from 'react';

interface RecipeCardProps {
    recipe: Recipe;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
    const [imageUrl, setImageUrl] = useState<string>('');

    useEffect(() => {
        getProxiedImageUrl(recipe.images)
            .then(url => setImageUrl(url))
            .catch(() => setImageUrl('')); // Handle error case
    }, [recipe.images]);

    return (
        <div className="recipe-card">
            {imageUrl && (
                <img
                    src={imageUrl}
                    alt={recipe.title}
                    className="recipe-image"
                />
            )}
            <div className="recipe-content">
                <h2 className="recipe-title">{recipe.title}</h2>
                <div className="recipe-meta">
                    <span>⏱️ {recipe.prep_time} mins</span>
                    <span>⭐ {recipe.rating.toFixed(1)}</span>
                </div>
            </div>
        </div>
    );
} 