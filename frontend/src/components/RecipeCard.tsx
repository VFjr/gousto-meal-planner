import { Recipe } from '../types';
import { getProxiedImageUrl } from '../utils/image';
import { useEffect, useState } from 'react';
import './RecipeCard.css';

interface RecipeCardProps {
    recipe: Recipe;
    isSingleRecipe?: boolean;
}

export function RecipeCard({ recipe, isSingleRecipe = false }: RecipeCardProps) {
    const [imageUrl, setImageUrl] = useState<string>('');
    const [isExpanded, setIsExpanded] = useState(isSingleRecipe);

    useEffect(() => {
        getProxiedImageUrl(recipe.images)
            .then(url => setImageUrl(url))
            .catch(() => setImageUrl(''));
    }, [recipe.images]);

    const handleCookbookClick = () => {
        window.open(`https://www.gousto.co.uk/cookbook/recipes/${recipe.slug}`, '_blank');
    };

    const handleCardClick = () => {
        if (!isSingleRecipe) {
            setIsExpanded(!isExpanded);
        }
    };

    return (
        <div
            className={`recipe-card ${isExpanded ? 'expanded' : ''} ${isSingleRecipe ? 'single' : ''}`}
            onClick={handleCardClick}
        >
            <div className="recipe-image-container">
                {imageUrl && (
                    <img
                        src={imageUrl}
                        alt={recipe.title}
                        className="recipe-image"
                    />
                )}
            </div>
            <div className="recipe-content">
                <h2 className="recipe-title">{recipe.title}</h2>
                <div className="recipe-meta">
                    <span>⏱️ {recipe.prep_time} mins</span>
                    <span>⭐ {recipe.rating?.toFixed(1) ?? 'N/A'}</span>
                </div>

                {isExpanded && (
                    <div className="recipe-actions" onClick={e => e.stopPropagation()}>
                        <button
                            className="action-button cookbook-button"
                            onClick={handleCookbookClick}
                        >
                            📖 View in Cookbook
                        </button>
                        <button className="action-button pdf-button">
                            📄 Generate PDF
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
} 